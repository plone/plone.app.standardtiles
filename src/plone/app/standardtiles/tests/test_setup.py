from plone import api
from plone.app.standardtiles.testing import PASTANDARDTILES_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import get_installer
from zope.component import getUtility

import unittest


PROJECTNAME = "plone.app.standardtiles"


class InstallTestCase(unittest.TestCase):

    layer = PASTANDARDTILES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_installed(self):
        qi = get_installer(self.portal, self.layer["request"])
        self.assertTrue(qi.is_product_installed(PROJECTNAME))


class UninstallTestCase(unittest.TestCase):

    layer = PASTANDARDTILES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.qi = get_installer(self.portal, self.layer["request"])
        self.qi.uninstall_product(PROJECTNAME)
        self.registry = getUtility(IRegistry)

    def test_uninstalled(self):
        self.assertFalse(self.qi.is_product_installed(PROJECTNAME))

    @unittest.expectedFailure
    def test_portletmanager_uninstalled(self):
        self.fail("TODO: Not Implemented")

    def filter_record(self, record):
        """Return a list of record items related with the project."""
        return [v for v in self.registry[record] if v.startswith(PROJECTNAME)]

    def test_registry_cleaned(self):

        self.assertEqual(self.filter_record("plone.app.tiles"), [])

        self.assertNotIn("plone.app.standardtiles.listing_views", self.registry)

        record = "plone.app.portlets.PortletManagerBlacklist"
        self.assertEqual(self.filter_record(record), [])
