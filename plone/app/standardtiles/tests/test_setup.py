# -*- coding: utf-8 -*-
from plone import api
from plone.app.standardtiles.testing import PASTANDARDTILES_INTEGRATION_TESTING  # noqa: E501

import unittest


PROJECTNAME = "plone.app.standardtiles"

try:
    from Products.CMFPlone.utils import get_installer
except Exception:
    get_installer = None


class InstallTestCase(unittest.TestCase):

    layer = PASTANDARDTILES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_installed(self):
        if get_installer:
            qi = get_installer(self.portal, self.layer["request"])
        else:
            qi = api.portal.get_tool("portal_quickinstaller")
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))


class UninstallTestCase(unittest.TestCase):

    layer = PASTANDARDTILES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.qi = get_installer(self.portal, self.layer["request"])
        else:
            self.qi = api.portal.get_tool("portal_quickinstaller")
        self.qi.uninstallProducts(products=[PROJECTNAME])

        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        self.registry = getUtility(IRegistry)

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    @unittest.expectedFailure
    def test_portletmanager_uninstalled(self):
        self.fail("TODO: Not Implemented")

    def filter_record(self, record):
        """Return a list of record items related with the project."""
        return [v for v in self.registry[record] if v.startswith(PROJECTNAME)]

    def test_registry_cleaned(self):

        self.assertEqual(self.filter_record("plone.app.tiles"), [])

        self.assertNotIn("plone.app.standardtiles.listing_views", self.registry)

        # XXX: I don't know what to do with change on
        # plone.app.querystring.interfaces.IQueryField

        record = "plone.app.portlets.PortletManagerBlacklist"
        self.assertEqual(self.filter_record(record), [])
