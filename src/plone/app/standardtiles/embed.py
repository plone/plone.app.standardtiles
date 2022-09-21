from plone.app.standardtiles import _PMF as _
from plone.memoize import ram
from plone.supermodel.model import Schema
from plone.tiles import Tile
from zope import schema

import requests


NOEMBED_ENDPOINT = "https://noembed.com/embed?url="


class IEmbedTile(Schema):
    """Embed tile."""

    media_url = schema.TextLine(title=_("Media URL"), required=True)


class EmbedTile(Tile):
    """A tile that embeds media."""

    @ram.cache(lambda method, obj: obj.data.get("media_url"))
    def __call__(self):
        media_url = self.data.get("media_url")
        url = NOEMBED_ENDPOINT + media_url
        rr = requests.get(url)
        if rr.ok:
            data = rr.json()
        return "<html><body>%s</body></html>" % data["html"]
