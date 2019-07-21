# -*- coding: utf-8 -*-
from datetime import datetime
from PIL import Image
from PIL import ImageDraw
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.standardtiles.testing import PASTANDARDTILES_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.textfield import RichTextValue
from plone.namedfile import NamedImage
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
from unittest import TestCase
from zope.component import createObject
from zope.component import queryUtility

import random
import six
import transaction


def image():
    img = Image.new(
        'RGB', (random.randint(320, 640), random.randint(320, 640))
    )
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        ((0, 0), img.size),
        fill=(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        ),
    )
    del draw
    output = six.BytesIO()
    img.save(output, 'PNG')
    output.seek(0)
    return output


class ExistingContentTileTests(TestCase):
    layer = PASTANDARDTILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portalURL = self.portal.absolute_url()

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD),
        )

        self.unprivileged_browser = Browser(self.layer['app'])

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        page_id = self.portal.invokeFactory(
            'Document',
            'a-simple-page',
            title=u'A simple page',
            description=u'A description',
        )
        self.page = self.portal[page_id]
        self.pageURL = self.portal[page_id].absolute_url()
        transaction.commit()

    def test_existing_content_tile(self):
        """The existing content tile takes the uuid of a content object in the
        site and displays the result of calling its default view's content-core
        macro

        """
        page_id = self.portal.invokeFactory(
            'Document',
            'an-another-page',
            title=u'An another page',
            description=u'A description',
            text=u'Hello World!',
        )
        self.portal[page_id].text = RichTextValue(u'Hello World!')

        page_uuid = IUUID(self.portal[page_id])

        transaction.commit()

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_text=True'
        )

        self.assertIn(u'Hello World!', self.unprivileged_browser.contents)

    def test_existing_content_tile_show_title(self):
        """
        """
        page_id = self.portal.invokeFactory(
            'Document',
            'an-another-page',
            title=u'An another page',
            description=u'A description',
            text=u'Hello World!',
        )
        self.portal[page_id].text = RichTextValue(u'Hello World!')

        page_uuid = IUUID(self.portal[page_id])

        transaction.commit()
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_title=True'
        )

        self.assertIn(u'An another page', self.unprivileged_browser.contents)

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
        )

        self.assertNotIn(
            u'An another page', self.unprivileged_browser.contents
        )

    def test_existing_content_tile_show_description(self):
        """
        """
        page_id = self.portal.invokeFactory(
            'Document',
            'an-another-page',
            title=u'An another page',
            description=u'A description',
            text=u'Hello World!',
        )
        self.portal[page_id].text = RichTextValue(u'Hello World!')

        page_uuid = IUUID(self.portal[page_id])

        transaction.commit()
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_description=True'
        )

        self.assertIn(u'A description', self.unprivileged_browser.contents)

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
        )

        self.assertNotIn(u'A description', self.unprivileged_browser.contents)

    def test_existing_content_tile_show_text(self):
        """
        """
        page_id = self.portal.invokeFactory(
            'Document',
            'an-another-page',
            title=u'An another page',
            description=u'A description',
            text=u'Hello World!',
        )
        self.portal[page_id].text = RichTextValue(u'Hello World!')

        page_uuid = IUUID(self.portal[page_id])

        transaction.commit()
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_text=True'
        )

        self.assertIn(u'Hello World!', self.unprivileged_browser.contents)

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
        )

        self.assertNotIn(u'Hello World!', self.unprivileged_browser.contents)

    def test_existing_content_tile_show_image(self):
        """
        """
        page_id = self.portal.invokeFactory(
            'Document',
            'a-page',
            title=u'A page',
            description=u'A description',
            text=u'Hello World!',
        )
        image_id = self.portal.invokeFactory(
            'Image',
            'an-image',
            title=u'An Image',
            description=u'foo',
            image=NamedImage(image(), 'image/png', filename=u'color.png'),
        )
        page_uuid = IUUID(self.portal[page_id])
        image_uuid = IUUID(self.portal[image_id])

        transaction.commit()
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_image=True'
        )
        self.assertNotIn(u'<img src="', self.unprivileged_browser.contents)

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + image_uuid
            + '&show_image=True'
        )

        self.assertIn(u'<img src="', self.unprivileged_browser.contents)

    def test_existing_content_tile_show_comments(self):
        """
        """
        # Allow discussion
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True

        page_id = self.portal.invokeFactory(
            'Document',
            'a-commented-page',
            title=u'A commented page',
            description=u'A description',
            text=u'Hello World!',
        )
        page = self.portal[page_id]
        page_uuid = IUUID(page)
        transaction.commit()
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_comments=True'
        )
        self.assertIn(u'0', self.unprivileged_browser.contents)

        conversation = IConversation(page)
        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'
        comment1.creator = 'jim'
        comment1.author_username = 'Jim'
        comment1.creation_date = datetime(2006, 9, 17, 14, 18, 12)
        comment1.modification_date = datetime(2006, 9, 17, 14, 18, 12)

        conversation.addComment(comment1)
        transaction.commit()
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_comments=True'
        )
        self.assertIn(u'1', self.unprivileged_browser.contents)

    def test_existing_content_tile_private(self):
        """When the current user does not have enough permissions to view
        the content linked to existing content tile, the tile renders
        empty"""
        self.portal.portal_workflow.setDefaultChain(
            'simple_publication_workflow'
        )

        page_id = self.portal.invokeFactory(
            'Document',
            'an-another-page',
            title=u'An another page',
            description=u'A description',
            text=RichTextValue(u'Hello World!'),
        )
        page_uuid = IUUID(self.portal[page_id])

        transaction.commit()

        self.unprivileged_browser.handleErrors = False
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
        )

        self.assertNotIn(u'Hello World!', self.unprivileged_browser.contents)
        self.assertIn(u'<body></body>', self.unprivileged_browser.contents)

    def test_edit_existing_content_tile(self):
        """The existing content tile takes the uuid of a content object in the
        site and displays the result of calling its default view's content-core
        macro

        """
        page_id = self.portal.invokeFactory('Document', 'an-another-page')
        page = self.portal[page_id]
        page_uuid = IUUID(page)
        page.text = RichTextValue(u'Hello World!')

        transaction.commit()

        self.browser.open(
            '{}/@@edit-tile/plone.app.standardtiles.existingcontent/unique'.format(
                page.absolute_url()
            )
        )
        self.browser.getControl(
            name='plone.app.standardtiles.existingcontent.content_uid'
        ).value = page_uuid
        self.browser.getControl(name='buttons.save').click()

        self.assertIn(u'not select the same content', self.browser.contents)

        page2_id = self.portal.invokeFactory(
            'Document',
            'an-another-page-2',
            title=u'An another page',
            description=u'A description',
            text=u'Hello World!',
        )
        page2 = self.portal[page2_id]
        page2_uuid = IUUID(page2)
        page2.text = RichTextValue(u'Hello World!')

        transaction.commit()

        self.browser.getControl(
            name='plone.app.standardtiles.existingcontent.content_uid'
        ).value = page2_uuid
        self.browser.getControl(name='buttons.save').click()
        self.assertIn(u'Hello World!', self.browser.contents)

    def test_existing_content_tile_cssclass(self):
        """The existing content tile takes the uuid of a content object in the
        site and displays the result of calling its default view's content-core
        macro

        """
        page_id = self.portal.invokeFactory(
            'Document',
            'an-another-page',
            title=u'An another page',
            description=u'A description',
        )

        page_uuid = IUUID(self.portal[page_id])

        transaction.commit()

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_title=True'
        )

        self.assertNotIn(u'extra-class', self.unprivileged_browser.contents)

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_title=True'
            + '&tile_class=extra-class'
        )

        self.assertIn(u'extra-class', self.unprivileged_browser.contents)

    def test_existing_content_tile_custom_layout(self):
        """
        Test that tile shows a custom layout, if set.
        If not set, it uses the default content layout
        """
        page_id = self.portal.invokeFactory(
            'Document',
            'a-page-for-test',
            title=u'An another page',
            description=u'A description',
        )
        self.portal[page_id].text = RichTextValue(u'Hello World!')

        page_uuid = IUUID(self.portal[page_id])

        transaction.commit()
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_text=True&view_template=custom_existingcontent_layout'
        )
        self.assertIn(
            u'This is a custom layout', self.unprivileged_browser.contents
        )
        self.assertIn(u'Hello World!', self.unprivileged_browser.contents)

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.existingcontent/unique?content_uid='
            + page_uuid
            + '&show_text=True'
        )

        self.assertNotIn(
            u'This is a custom layout', self.unprivileged_browser.contents
        )
        self.assertIn(u'Hello World!', self.unprivileged_browser.contents)
