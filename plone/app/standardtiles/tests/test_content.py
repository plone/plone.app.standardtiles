# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from lxml import html
from plone.app.standardtiles.image import HAS_PLONE_5
from plone.app.standardtiles.testing import EDITOR_USER_NAME
from plone.app.standardtiles.testing import EDITOR_USER_PASSWORD
from plone.app.standardtiles.testing import PASTANDARDTILES_FUNCTIONAL_TESTING  # noqa
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.locking.interfaces import ILockable
from plone.testing.z2 import Browser
from unittest import TestCase
import transaction

def fromstring(s):
    html_parser = html.HTMLParser(encoding='utf-8')
    return html.fromstring(s, parser=html_parser).getroottree().getroot()

if HAS_PLONE_5:
    from z3c.relationfield import RelationValue
    from zope.component import getUtility
    from zope.intid import IIntIds


class ContentTileTests(TestCase):
    """Here we show up the main tiles used for the content usage.

    """
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

        self.other_browser = Browser(self.layer['app'])
        self.other_browser.handleErrors = False
        self.other_browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (EDITOR_USER_NAME, EDITOR_USER_PASSWORD,)
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

    def test_document_actions_tile(self):
        """The document actions tile just lists the actions registered in the
        document_actions category.

        """
        # We make sure at least the print action visibility is on:

        action_tool = getToolByName(self.portal, 'portal_actions')
        print_action = action_tool.document_actions.get('print')
        print_action.visible = True
        transaction.commit()

        self.unprivileged_browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.document_actions'
        )

        self.assertIn('document-action-print',
                      self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="document-action-print"]')
        self.assertEqual(len(nodes), 1)

    def test_keywords_tile(self):
        """The keywords tile displays a list of the keywords (aka subjects)
        assigned to the context.

        """
        # We will use the page we created before for the tests. Since we have not
        # added any keyword to it yet, the tile contents are empty:

        self.unprivileged_browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.keywords'
        )

        self.assertNotIn('category', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="category"]')
        self.assertEqual(len(nodes), 0)

        # If we now add some keywords to it:
        try:
            self.page.setSubject(('Statues', 'Sprint'))  # AT
        except AttributeError:
            self.page.subject = ('Statues', 'Sprint')  # DX
        transaction.commit()

        # The tile will show them:
        self.unprivileged_browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.keywords'
        )

        self.assertIn('category', self.unprivileged_browser.contents)
        self.assertIn('Sprint', self.unprivileged_browser.contents)
        self.assertIn('Statues', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="category"]')
        self.assertEqual(len(nodes), 1)

    def test_related_items_tiles(self):
        self.browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.related_items'
        )

        self.assertNotIn('relatedItems', self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@class="relatedItems"]')
        self.assertEqual(len(nodes), 0)

        self.portal.invokeFactory('Document', 'doc1', title='Document 1')
        self.portal.invokeFactory('Document', 'doc2', title='Document 2')
        if HAS_PLONE_5:
            int_ids = getUtility(IIntIds)
            self.page.relatedItems = [
                RelationValue(int_ids.getId(self.portal.doc1)),
                RelationValue(int_ids.getId(self.portal.doc2))
            ]
        else:
            self.page.setRelatedItems([
                self.portal.doc1,
                self.portal.doc2
            ])

        transaction.commit()

        self.browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.related_items'
        )

        self.assertIn('relatedItems', self.browser.contents)
        self.assertIn('Document 1', self.browser.contents)
        self.assertIn('Document 2', self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@class="relatedItems"]')
        self.assertEqual(len(nodes), 1)

        if HAS_PLONE_5:
            nodes = root.xpath('//body//*[@class="relatedItems"]//ul/li')
        else:
            nodes = root.xpath('//body//*[@class="relatedItems"]//dl/dd')
        self.assertEqual(len(nodes), 2)

    def test_history_tile(self):
        # First edit a page so we have an edit history:
        self.browser.open(self.pageURL + '/edit')

        if HAS_PLONE_5:
            self.browser.getControl(name='form.widgets.IDublinCore.title').value = 'A different title'  # noqa
        else:
            self.browser.getControl(name='title').value = 'A different title'
        self.browser.getControl(label='Save').click()
        self.assertIn('A different title', self.browser.contents)

        # The tile will show them:
        self.browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.history'
        )

        self.assertIn('content-history', self.browser.contents)
        self.assertIn('historyAction state-Edited', self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="content-history"]')
        self.assertEqual(len(nodes), 1)

        nodes = root.xpath('//body//*[@class="historyAction state-Edited"]')
        self.assertLessEqual(2, len(nodes))

    def test_lockinfo_tile(self):
        self.other_browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.lockinfo'
        )

        self.assertIn('plone-lock-status', self.other_browser.contents)

        root = fromstring(self.other_browser.contents)
        nodes = root.xpath('//body//*[@id="plone-lock-status"]')
        self.assertEqual(len(nodes), 1)
        self.assertEqual(0, len(nodes[0].getchildren()))

        # Then lock the page:
        lockable = ILockable(self.page)
        lockable.lock()
        transaction.commit()

        # The tile will show them:
        self.other_browser.open(
            self.pageURL
            + '/@@plone.app.standardtiles.lockinfo'
        )

        self.assertIn('plone-lock-status', self.other_browser.contents)

        root = fromstring(self.other_browser.contents)
        nodes = root.xpath('//body//*[@id="plone-lock-status"]')
        self.assertEqual(len(nodes), 1)
        self.assertGreaterEqual(len(nodes[0].getchildren()), 1)
