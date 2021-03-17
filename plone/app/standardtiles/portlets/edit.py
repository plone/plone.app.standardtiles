# -*- coding: utf-8 -*-
from plone.app.tiles.browser.edit import DefaultEditView
from plone.portlets.utils import unhashPortletInfo
from plone.uuid.interfaces import IUUIDGenerator
from six.moves import urllib
from zope.component import getUtility


class PortletTileEditView(DefaultEditView):
    """Override the tile edit view for the portlet tile and redirect it to the
    portlet edit view.
    """

    def __call__(self):
        portlet_hash = self.request["portlet_hash"]
        info = unhashPortletInfo(portlet_hash)
        url = (
            "{0}/++contextportlets++plone.app.standardtiles.portletManager/"
            "{1}/edit".format(self.context.absolute_url(), info["name"])
        )
        if not self.tileId:
            generator = getUtility(IUUIDGenerator)
            tileId = generator()
        else:
            tileId = self.tileId

        typeName = "plone.app.standardtiles.portlet"
        tile_url = "{0}/@@{1}/{2}?portlet_hash={3}".format(
            self.context.absolute_url(), typeName, tileId, portlet_hash
        )
        self.request.form["referer"] = tile_url
        self.request.response.redirect(
            "{0}?referer={0}".format(url, urllib.parse.quote(tile_url))
        )
