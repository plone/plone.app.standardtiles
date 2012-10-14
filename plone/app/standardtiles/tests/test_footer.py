# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.component import queryUtility
from plone.tiles.interfaces import ITileType
from plone.app.standardtiles.testing import STANDARD_TILE_INTEGRATION_TESTING


class FooterTileIntegrationTest(unittest.TestCase):
    layer = STANDARD_TILE_INTEGRATION_TESTING

    def test_tiletype_registration(self):
        self.assertTrue(queryUtility(ITileType, name='footer.texttile'))
        self.assertEqual(
            queryUtility(ITileType, name='footer.texttile').title,
            "Footer Editable Texttile")
