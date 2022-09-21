from lxml import html
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.standardtiles.testing import PASTANDARDTILES_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.interfaces import ISiteSchema
from unittest import TestCase
from zope.component import queryUtility

import transaction


def fromstring(s):
    html_parser = html.HTMLParser(encoding="utf-8")
    return html.fromstring(s, parser=html_parser).getroottree().getroot()


class TestLayoutTiles(TestCase):
    """Here we show up the main tiles used for the page layout."""

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

        self.registry = queryUtility(IRegistry)

    def test_colophon_tile(self):
        return
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.colophon"
        )
        # colophon is hidden by default in Plone 5
        self.assertNotIn("portal-colophon", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="portal-colophon"]')
        self.assertEqual(len(nodes), 0)

    def test_footer_tile(self):
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.footer"
        )

        self.assertIn("portal-footer", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="portal-footer-signature"]')
        self.assertEqual(len(nodes), 1)

    def test_site_actions_tile(self):
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.site_actions"
        )
        # site-actions are hidden by default in Plone 5
        self.assertNotIn("portal-siteactions", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="portal-siteactions"]')
        self.assertEqual(len(nodes), 0)

    def test_empty_analytics_tile(self):
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.analytics"
        )

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath("//body//script")
        self.assertEqual(len(nodes), 0)

    def test_analytics_tile(self):
        snippet = "<script type='text/javascript'> var _gaq = _gaq || []; _gaq.push(['_setAccount', 'UA-XXXXX-X']); _gaq.push(['_trackPageview']); (function() { var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true; ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s); })();</script>"
        site_settings = self.registry.forInterface(ISiteSchema, prefix="plone")
        site_settings.webstats_js = snippet
        transaction.commit()

        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.analytics"
        )

        self.assertIn("<script", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath("//body//script")
        self.assertEqual(len(nodes), 1)

    def test_anontools_tile(self):
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.anontools"
        )

        self.assertIn("Log in", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//a[@title="Log in"]')
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text.strip(), "Log in")

    def test_logo_tile(self):
        self.browser.open(self.portalURL + "/@@plone.app.standardtiles.logo")

        self.assertIn("portal-logo", self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="portal-logo"]')
        self.assertEqual(len(nodes), 1)

    def test_global_sections_tile(self):
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.global_sections"
        )

        self.assertIn("portal-globalnav", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="portal-globalnav"]')
        self.assertEqual(len(nodes), 1)

    def test_path_bar_tile(self):
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.path_bar"
        )

        self.assertIn("portal-breadcrumbs", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="portal-breadcrumbs"]')
        self.assertEqual(len(nodes), 1)

    def test_edit_bar_tile(self):
        self.browser.open(self.portalURL + "/@@plone.app.standardtiles.edit_bar")

        self.assertIn("edit-bar", self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="edit-bar"]')
        self.assertEqual(len(nodes), 1)

    def test_table_of_contents_tile(self):
        self.page.table_of_contents = True

        transaction.commit()

        self.unprivileged_browser.open(
            self.pageURL + "/@@plone.app.standardtiles.tableofcontents"
        )

        self.assertIn("document-toc", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="document-toc"]')
        self.assertEqual(len(nodes), 1)

    def test_searchbox_tile(self):
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.searchbox"
        )

        self.assertIn("portal-searchbox", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="portal-searchbox"]')
        self.assertEqual(len(nodes), 1)

    def test_language_tile(self):
        """The language selector tile shows a list of languages available in
        the site. Since the language selection depends on cookies, this tile
        will be only available if the corresponding setting is set in the
        self.portal_languages tool.

        """
        # By default, the selector won't show up::
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.languageselector"
        )

        self.assertNotIn("portal-languageselector", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="portal-languageselector"]')
        self.assertEqual(len(nodes), 0)

        # Adding supported languages will show them in the tile::
        lt = getToolByName(self.portal, "portal_languages")
        lt.addSupportedLanguage("ca")
        lt.settings.always_show_selector = True
        transaction.commit()

        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.languageselector"
        )

        # langauge selector is empty by default in Plone 5
        self.assertNotIn("portal-languageselector", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="portal-languageselector"]')
        self.assertEqual(len(nodes), 0)

        nodes = root.xpath('//body//*[@class="language-ca"]')
        self.assertEqual(len(nodes), 0)

    def test_nextprevious_tile(self):
        """The next previous tile shows a next and a previous button if there
        is a next or a previous object. It can be activated by checking the
        checkbox in the schema (edit).

        """
        # Let's add a folder and add three pages for testing the tile::
        self.portal.invokeFactory(
            "Folder", "next-previous-folder", title="Next Previous folder"
        )
        folder = self.portal.get("next-previous-folder")

        folder.invokeFactory("Document", "page-one", title="Page one")
        page1 = folder.get("page-one")

        folder.invokeFactory("Document", "page-two", title="Page two")
        folder.get("page-two")

        folder.invokeFactory("Document", "page-three", title="Page three")
        folder.get("page-three")

        transaction.commit()

        # Test the tile on the first page. It should not be there since next
        # previous is still disabled (default configuration).
        self.assertFalse(
            page1.restrictedTraverse("@@plone_nextprevious_view").enabled()
        )

        self.unprivileged_browser.open(
            self.portalURL
            + "/next-previous-folder/page-one/@@plone.app.standardtiles.nextprevious"
        )

        self.assertNotIn("div", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath("//body/div")
        self.assertEqual(len(nodes), 0)

        # Then we activate next previous and we should see a next-link when
        # rendering the tile on the first page::

        folder.nextPreviousEnabled = True
        transaction.commit()

        self.assertTrue(page1.restrictedTraverse("@@plone_nextprevious_view").enabled())

        self.unprivileged_browser.open(
            self.portalURL
            + "/next-previous-folder/page-one/@@plone.app.standardtiles.nextprevious"
        )

        self.assertIn("<link", self.unprivileged_browser.contents)
        self.assertIn('title="Go to next item"', self.unprivileged_browser.contents)
        self.assertNotIn(
            'title="Go to previous item"', self.unprivileged_browser.contents
        )

        root = fromstring(self.unprivileged_browser.contents)

        nodes = root.xpath('//head/link[@rel="next"]')
        self.assertEqual(len(nodes), 1)

        nodes = root.xpath('//head/link[@rel="previous"]')
        self.assertEqual(len(nodes), 0)

        self.unprivileged_browser.open(
            self.portalURL
            + "/next-previous-folder/page-two/@@plone.app.standardtiles.nextprevious"
        )

        self.assertIn("<link", self.unprivileged_browser.contents)
        self.assertIn('title="Go to next item"', self.unprivileged_browser.contents)
        self.assertIn('title="Go to previous item"', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)

        nodes = root.xpath('//head/link[@rel="next"]')
        self.assertEqual(len(nodes), 1)

        nodes = root.xpath('//head/link[@rel="previous"]')
        self.assertEqual(len(nodes), 1)

        self.unprivileged_browser.open(
            self.portalURL
            + "/next-previous-folder/page-three/@@plone.app.standardtiles.nextprevious"
        )

        self.assertIn("<link", self.unprivileged_browser.contents)
        self.assertNotIn('title="Go to next item"', self.unprivileged_browser.contents)
        self.assertIn('title="Go to previous item"', self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)

        nodes = root.xpath('//head/link[@rel="next"]')
        self.assertEqual(len(nodes), 0)

        nodes = root.xpath('//head/link[@rel="previous"]')
        self.assertEqual(len(nodes), 1)

    def test_login_tile(self):
        # For a logged-in user, the login tile should be empty
        self.browser.open(self.portalURL + "/@@plone.app.standardtiles.login")

        self.assertNotIn("loginform", self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="loginform"]')
        self.assertEqual(len(nodes), 0)

        # When we are not logged in, we should get the form::
        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.login"
        )

        self.assertIn("loginform", self.unprivileged_browser.contents)
        self.assertNotIn("@@register", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//*[@id="loginform"]')
        self.assertEqual(len(nodes), 1)

        # By default, we should not have the "register" link in there::

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//a[@href="http://nohost/plone/@@register"]')
        self.assertEqual(len(nodes), 0)

        # But if we enable self-registration, it should show up::

        security_settings = ISecuritySchema(self.portal)
        security_settings.set_enable_self_reg(True)
        transaction.commit()

        self.unprivileged_browser.open(
            self.portalURL + "/@@plone.app.standardtiles.login"
        )

        self.assertIn("@@register", self.unprivileged_browser.contents)

        root = fromstring(self.unprivileged_browser.contents)
        nodes = root.xpath('//body//a[@href="http://nohost/plone/@@register"]')
        self.assertEqual(len(nodes), 1)

    def test_discussion_tile(self):
        """Discussion tile is visible only when discussion is enabled"""
        self.browser.open(self.pageURL + "/@@plone.app.standardtiles.discussion")

        self.assertNotIn("<form", self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath("//body//form")
        self.assertEqual(len(nodes), 0)

        self.registry.forInterface(IDiscussionSettings).globally_enabled = True
        self.page.allow_discussion = True

        transaction.commit()

        self.browser.open(self.pageURL + "/@@plone.app.standardtiles.discussion")

        self.assertIn("<form", self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath("//body//form")
        self.assertEqual(len(nodes), 1)
