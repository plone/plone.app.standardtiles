# -*- coding: utf-8 -*-
from zope.component import getUtility
from plone.uuid.interfaces import IUUIDGenerator

from plone.portlets.utils import unhashPortletInfo
from plone.app.tiles.browser.edit import DefaultEditView

import urllib


class PortletTileEditView(DefaultEditView):
    """ Override the tile edit view for the portlet tile and redirect it to the
        portlet edit view.
    """
    def __call__(self):
        portlet_hash = self.request['portlet_hash']
        info = unhashPortletInfo(portlet_hash)
        url = '{}/++contextportlets++plone.app.standardtiles.portletManager/{}/edit'.format(self.context.absolute_url(), info['name'])

        if not self.tileId:
            generator = getUtility(IUUIDGenerator)
            tileId = generator()
        else:
            tileId = self.tileId

        typeName = 'plone.app.standardtiles.portlet'
        tile_url = '{}/@@{}/{}?portlet_hash={}'.format(self.context.absolute_url(), typeName, tileId, portlet_hash)

        self.request.form['referer'] = tile_url
        self.request.response.redirect('{}?referer={}'.format(url, urllib.quote(tile_url)))
