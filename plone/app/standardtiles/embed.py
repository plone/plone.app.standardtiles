# -*- coding: utf-8 -*-

from plone.app.standardtiles import _PMF as _
from plone.supermodel.model import Schema
from plone.tiles import Tile
from zope import schema

import requests

NOEMBED_ENDPOINT = 'https://noembed.com/embed?callback=embed_data=&url='


class IEmbedTile(Schema):
    """ Embed tile.
    """

    media_url = schema.TextLine(
        title=_(u"Media URL"),
        required=True
    )


class EmbedTile(Tile):
    """ A tile that embeds media.
    """

    def __call__(self):
        media_url = self.data.get('media_url')
        url = NOEMBED_ENDPOINT + media_url
        rr = requests.get(url)
        if rr.ok:
            data = rr.json()
        return u"<html><body>%s</body></html>" % data['html']
