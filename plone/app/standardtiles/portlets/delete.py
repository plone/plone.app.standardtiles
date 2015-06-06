# -*- coding: utf-8 -*-

from plone.app.tiles.browser.delete import DefaultDeleteView


class PortletTileDeleteView(DefaultDeleteView):
    """ Override the tile edit view for the portlet tile and redirect it to the
        portlet edit view.
    """

    def __call__(self):
        result = super(PortletTileDeleteView, self).__call__()
        # delete the portlet
        # TODO

