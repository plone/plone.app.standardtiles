from lxml import html
from persistent.dict import PersistentDict
from PIL import Image
from PIL import ImageDraw
from plone.app.standardtiles.embed import NOEMBED_ENDPOINT
from plone.app.standardtiles.html import HTMLTile
from plone.app.standardtiles.testing import PASTANDARDTILES_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.namedfile import NamedFile
from plone.testing.zope import Browser
from unittest import TestCase
from urllib.parse import quote
from zope.annotation import IAnnotations

import io
import os
import pkg_resources
import plone.app.standardtiles.tests as test_dir
import random
import transaction
import unittest


try:
    pkg_resources.get_distribution("plone.formwidget.multifile")
except pkg_resources.DistributionNotFound:
    HAS_MULTIFILE = False
else:
    HAS_MULTIFILE = True


def fromstring(s):
    html_parser = html.HTMLParser(encoding="utf-8")
    return html.fromstring(s, parser=html_parser).getroottree().getroot()


def image():
    img = Image.new("RGB", (random.randint(320, 640), random.randint(320, 640)))
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        ((0, 0), img.size),
        fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
    )
    del draw

    output = io.BytesIO()
    img.save(output, "PNG")
    output.seek(0)

    return output


class ContentTileTests(TestCase):
    layer = PASTANDARDTILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portalURL = self.portal.absolute_url()

        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )

        self.unprivileged_browser = Browser(self.layer["app"])

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        page_id = self.portal.invokeFactory(
            "Document",
            "a-simple-page",
            title="A simple page",
            description="A description",
        )
        self.page = self.portal[page_id]
        self.pageURL = self.portal[page_id].absolute_url()
        transaction.commit()

    def test_embed_tile(self):
        """The embed tile is a transient tile which takes a media URL and
        displays the associated embedded code::
        """
        media_url = "http://www.youtube.com/watch?v=ayPKvFNz8aE"

        self.unprivileged_browser.open(
            self.portalURL
            + "/@@plone.app.standardtiles.embed/unique?media_url="
            + quote(media_url)
        )

        self.assertIn(NOEMBED_ENDPOINT + media_url, self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath("//body/p")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, NOEMBED_ENDPOINT + media_url)

    def test_rawembed_tile(self):
        """The rawembed tile display a html snippet with title::"""
        tile_title = "Hello"
        html_snippet = "<strong>Hello</strong>"
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.rawembed/unique",
            data="html_snippet="
            + quote(html_snippet)
            + "&tile_title="
            + quote(tile_title),
        )
        contents = self.unprivileged_browser.contents
        self.assertTrue(tile_title in contents)
        self.assertTrue(html_snippet in contents)

    def test_navigation_tile(self):
        """The navigation tree tile displays a navigation tree for the context
        where it's inserted and take no configuration parameters.

        Rendering this tile in the site root should show the document we
        created before:

        """
        self.browser.open(self.portalURL + "/@@plone.app.standardtiles.navigation")

        self.assertIn("A simple page", self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//ul[@class="navTree navTreeLevel0"]/li')
        self.assertEqual(len(nodes), 1)

    def test_sitemap_tile(self):
        """The sitemap tile displays a sitemap for the site.

        Rendering this tile in the site root should show the document we
        created before:

        """
        self.browser.open(self.portalURL + "/@@plone.app.standardtiles.sitemap")

        self.assertIn("A simple page", self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//ul[@class="navTree navTreeLevel0"]/li')
        self.assertEqual(len(nodes), 1)  # Only simple page

    @unittest.skipIf(
        not HAS_MULTIFILE,
        "plone.formwidget.multifile is not available",
    )
    def test_attachment_tile(self):
        """This persistent tile renders a link pointing to a file stored in the
        tile data itself.

        """
        annotations = IAnnotations(self.page)
        annotations["plone.tiles.data.test"] = PersistentDict(
            {
                "files": [
                    NamedFile("Hello World!", "text/plain", "hello_world.txt"),
                    NamedFile("Foobar!", "text/plain", "foobar.txt"),
                ]
            }
        )

        transaction.commit()

        self.browser.open(self.pageURL + "/@@plone.app.standardtiles.attachment/test")

        self.assertIn("hello_world.txt", self.browser.contents)
        self.assertIn("foobar.txt", self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath("//body//a")
        self.assertEqual(len(nodes), 2)

        self.browser.getLink(index=1).click()
        self.assertEqual(self.browser.contents, "Foobar!")

    def test_rss_tile(self):
        """This tile shows the first five items in a RSS feed."""
        # Use the RSS stored in the test directory, this way we don't have an
        # external dependency.
        dirname = os.path.dirname(test_dir.__file__)
        path = "file://{}".format(os.path.join(dirname, "RSS.xml"))

        # Create the RSS tile, with the local RSS URI:
        self.unprivileged_browser.open(
            self.portalURL
            + "/@@plone.app.standardtiles.rss/unique?url="
            + quote(path)
            + "&portlet_title=TEST_RSS_TILE"
        )

        self.assertIn("TEST_RSS_TILE", self.unprivileged_browser.contents)

        self.assertIn(
            ' href="http://localhost:55440/plone/doc-one"',
            self.unprivileged_browser.contents,
        )

    def test_html_tile_unicode(self):
        tile = HTMLTile(self.portal, self.layer["request"])
        tile.__name__ = "test.html.tile"
        tile.data["content"] = "<p>Hello Wörld!</p>"
        self.assertEqual(tile(), "<html><body><p>Hello Wörld!</p></body></html>")

    def test_html_tile_utf8(self):
        tile = HTMLTile(self.portal, self.layer["request"])
        tile.__name__ = "test.html.tile"
        tile.data["content"] = "<p>Hello Wörld!</p>".encode()
        self.assertEqual(tile(), "<html><body><p>Hello Wörld!</p></body></html>")
