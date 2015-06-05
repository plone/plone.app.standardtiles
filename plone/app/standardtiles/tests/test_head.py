# -*- coding: utf-8 -*-
from lxml import html
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.app.standardtiles.testing import PASTANDARDTILES_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from unittest import TestCase
import transaction

try:
    from Products.CMFPlone.interfaces import ISecuritySchema
    from Products.CMFPlone.interfaces import ISiteSchema
    HAS_PLONE_5 = True
except ImportError:
    from plone.app.controlpanel.security import ISecuritySchema
    HAS_PLONE_5 = False

def fromstring(s):
    html_parser = html.HTMLParser(encoding='utf-8')
    return html.fromstring(s, parser=html_parser).getroottree().getroot()


class TestHeadTiles(TestCase):
    """A field tile is a very simple tile: it just displays a field of its
    context honoring the widget customizations present in the schema tagged
    values; but it doesn't take into account the other tagged values such as
    when to display something or not, as this is both useless from a tile
    point-of-view, and causes harm due to certain default settings of
    behaviours.

    """
    layer = PASTANDARDTILES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portalURL = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,)
        )

        self.unprivileged_browser = Browser(self.layer['app'])

    def test_title_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.headtitle'
        )

        self.assertIn('<title', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/title')
        self.assertEqual(len(nodes), 1)

    def test_stylesheets_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.stylesheets'
        )

        self.assertIn('<link', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/link[@rel="stylesheet"]')
        self.assertGreaterEqual(len(nodes), 1)

    def test_javascripts_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.javascripts'
        )

        self.assertIn('<script', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/script')
        self.assertGreaterEqual(len(nodes), 1)

    def test_favicon_link_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.faviconlink'
        )

        self.assertIn('<link', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/link[@rel="shortcut icon"]')
        self.assertEqual(len(nodes), 1)

    def test_search_link_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.searchlink'
        )

        self.assertIn('<link', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/link[@rel="search"]')
        self.assertEqual(len(nodes), 1)

    def test_navigation_link_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.navigationlink'
        )

        self.assertIn('<link', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/link[@rel="home"]')
        self.assertEqual(len(nodes), 1)

        nodes = root.xpath('//head/link[@rel="contents"]')
        self.assertEqual(len(nodes), 1)

    def test_rss_link_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.rsslink'
        )

        self.assertIn('<link', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/link[@type="application/rss+xml"]')
        self.assertGreaterEqual(len(nodes), 1)

    def test_canonical_url_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.canonical_url'
        )

        self.assertIn('<link', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/link[@rel="canonical"]')
        self.assertEqual(len(nodes), 1)

    def test_author_link_tile(self):
        self.browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.authorlink'
        )

        self.assertIn('<link', self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//head/link[@rel="author"]')
        self.assertEqual(len(nodes), 1)

    def test_dublincore_tile(self):
        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.dublincore'
        )

        self.assertNotIn('<meta', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/meta')
        self.assertEqual(len(nodes), 0)

        registry = getUtility(IRegistry)
        if HAS_PLONE_5:
            site_settings = registry.forInterface(ISiteSchema, prefix="plone")
            site_settings.exposeDCMetaTags = True
        else:
            ptool = getToolByName(self.portal, 'portal_properties')
            ptool.site_properties.exposeDCMetaTags = True

        security_settings = ISecuritySchema(self.portal)
        security_settings.set_allow_anon_views_about(True)

        transaction.commit()

        self.unprivileged_browser.open(
            self.portalURL
            + '/@@plone.app.standardtiles.dublincore'
        )

        self.assertIn('<meta', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//head/meta')
        self.assertGreaterEqual(len(nodes), 1)
