from plone.app.tiles.browser.edit import DefaultEditView
from plone.portlets.utils import unhashPortletInfo
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getUtility

import urllib


class PortletTileEditView(DefaultEditView):
    """Override the tile edit view for the portlet tile and redirect it to the
    portlet edit view.
    """

    def __call__(self):
        portlet_hash = self.request["portlet_hash"]
        info = unhashPortletInfo(portlet_hash)
        url = (
            "{}/++contextportlets++plone.app.standardtiles.portletManager/"
            "{}/edit".format(self.context.absolute_url(), info["name"])
        )
        if not self.tileId:
            generator = getUtility(IUUIDGenerator)
            tileId = generator()
        else:
            tileId = self.tileId

        typeName = "plone.app.standardtiles.portlet"
        tile_url = "{}/@@{}/{}?portlet_hash={}".format(
            self.context.absolute_url(), typeName, tileId, portlet_hash
        )
        self.request.form["referer"] = tile_url
        self.request.response.redirect(f"{url}?referer={urllib.parse.quote(tile_url)}")
