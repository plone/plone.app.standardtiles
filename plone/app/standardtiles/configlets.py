# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.tiles.tile import Tile


class ConfigletsTile(Tile):
    """A tile displaying the list of available configlets."""

    def controlPanel(self):
        return getToolByName(self.context, 'portal_controlpanel')
