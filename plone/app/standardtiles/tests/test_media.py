# -*- coding: utf-8 -*-
from PIL import Image
from PIL import ImageDraw
from lxml import html
from persistent.dict import PersistentDict
from plone.app.textfield import RichTextValue
from plone.app.standardtiles.embed import NOEMBED_ENDPOINT
from plone.app.standardtiles.testing import HAS_PLONE_5
from plone.app.standardtiles.testing import PASTANDARDTILES_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.namedfile import NamedFile, NamedImage
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
from unittest import TestCase
from urllib import quote
from zope.annotation import IAnnotations
import StringIO
import os
import plone.app.standardtiles.tests as test_dir
import random
import transaction


def fromstring(s):
    html_parser = html.HTMLParser(encoding='utf-8')
    return html.fromstring(s, parser=html_parser).getroottree().getroot()


def image():
    img = Image.new('RGB', (random.randint(320, 640),
                            random.randint(320, 640)))
    draw = ImageDraw.Draw(img)
    draw.rectangle(((0, 0), img.size), fill=(random.randint(0, 255),
                                             random.randint(0, 255),
                                             random.randint(0, 255)))
    del draw

    output = StringIO.StringIO()
    img.save(output, 'PNG')
    output.seek(0)

    return output


class ContentTileTests(TestCase):
    layer = PASTANDARDTILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portalURL = self.portal.absolute_url()

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,)
        )

        self.unprivileged_browser = Browser(self.layer['app'])

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        page_id = self.portal.invokeFactory(
            'Document', 'a-simple-page',
            title=u'A simple page', description=u'A description'
        )
        self.page = self.portal[page_id]
        self.pageURL = self.portal[page_id].absolute_url()
        transaction.commit()

    def test_embed_tile(self):
        """The embed tile is a transient tile which takes a media URL and
        displays the associated embedded code::
        """
        media_url = 'http://www.youtube.com/watch?v=ayPKvFNz8aE'

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.embed/unique?media_url='
            + quote(media_url)
        )

        self.assertIn(NOEMBED_ENDPOINT + media_url,
                      self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body/p')
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, NOEMBED_ENDPOINT + media_url)

    def test_existing_content_tile(self):
        """The existing content tile takes the uuid of a content object in the
        site and displays the result of calling its default view's content-core
        macro

        """
        page_id = self.portal.invokeFactory(
            'Document', 'an-another-page',
            title=u'An another page', description=u'A description',
            text=u'Hello World!'
        )
        if HAS_PLONE_5:
            self.portal[page_id].text = RichTextValue(u'Hello World!')

        page_uuid = IUUID(self.portal[page_id])

        transaction.commit()

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
        )

        self.assertIn(u'Hello World!', self.unprivileged_browser.contents)

    def test_navigation_tile(self):
        """The navigation tree tile displays a navigation tree for the context
        where it's inserted and take no configuration parameters.

        Rendering this tile in the site root should show the document we
        created before:

        """
        self.browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.navigation'
        )

        self.assertIn('A simple page', self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//ul[@class="navTree navTreeLevel0"]/li')
        self.assertEqual(len(nodes), 1)

    def test_sitemap_tile(self):
        """The sitemap tile displays a sitemap for the site.

        Rendering this tile in the site root should show the document we
        created before:

        """
        self.browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.sitemap'
        )

        self.assertIn('A simple page', self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//ul[@class="navTree navTreeLevel0"]/li')
        self.assertEqual(len(nodes), 1)  # Only simple page

    def test_attachment_tile(self):
        """This persistent tile renders a link pointing to a file stored in the
        tile data itself.

        """
        annotations = IAnnotations(self.page)
        annotations['plone.tiles.data.test'] = PersistentDict({
            'files': [
                NamedFile(u'Hello World!', 'text/plain', u'hello_world.txt'),
                NamedFile(u'Foobar!', 'text/plain', u'foobar.txt')
            ]
        })

        transaction.commit()

        self.browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.attachment/test'
        )

        self.assertIn(u'hello_world.txt', self.browser.contents)
        self.assertIn(u'foobar.txt', self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//a')
        self.assertEqual(len(nodes), 2)

        self.browser.getLink(index=1).click()
        self.assertEqual(self.browser.contents, u'Foobar!')

    def test_rss_tile(self):
        """This tile shows the first five items in a RSS feed.

        """
        # Use the RSS stored in the test directory, this way we don't have an
        # external dependency.
        dirname = os.path.dirname(test_dir.__file__)
        path = 'file://{0}'.format(os.path.join(dirname, 'RSS.xml'))

        # Create the RSS tile, with the local RSS URI:
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.rss/unique?url='
            + quote(path)
            + '&portlet_title=TEST_RSS_TILE'
        )

        self.assertIn('TEST_RSS_TILE', self.unprivileged_browser.contents)

        self.assertIn(
            '<a href="http://localhost:55440/plone/doc-one" class="tile">',
            self.unprivileged_browser.contents
        )

    def test_image_tile(self):
        annotations = IAnnotations(self.page)
        annotations['plone.tiles.data.test'] = PersistentDict({
            'image': NamedImage(image(), 'image/png', filename=u'color.png')
        })

        transaction.commit()

        self.browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.image/test'
        )

        # Confirm pass CSRF protection on Plone 5
        try:
            self.browser.getControl(name='form.button.confirm').click()
        except LookupError:
            pass

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//img')
        self.assertEqual(len(nodes), 1)

    def test_rawhtml_tile(self):
        annotations = IAnnotations(self.page)
        annotations['plone.tiles.data.test'] = PersistentDict({
            'content': '<p>Hello World!</p>'
        })

        transaction.commit()

        self.browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.rawhtml/test'
        )

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body/p')
        self.assertEqual(nodes[0].text, 'Hello World!')
