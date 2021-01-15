# -*- coding: utf-8 -*-
from plone.app.standardtiles import _PMF as _
from plone.app.standardtiles import embed_providers
from plone.memoize import ram
from plone.supermodel.model import Schema
from plone.tiles import Tile
from zope import schema

import oembed

try:
    from urllib.error import HTTPError
except ImportError:  # py2
    from urllib2 import HTTPError


CONSUMER = oembed.OEmbedConsumer()
ENABLED_PROVIDERS = []
DISABLED_PROVIDERS = []

for endpoint, scheme in embed_providers.PROVIDERS:
    try:
        oe = oembed.OEmbedEndpoint(endpoint, scheme)
        ENABLED_PROVIDERS.append(endpoint)
    except:  # noqa
        # Some endpoints fail to register
        DISABLED_PROVIDERS.append(endpoint)
        continue
    CONSUMER.addEndpoint(oe)


class IEmbedTile(Schema):
    """ Embed tile.
    """

    media_url = schema.TextLine(
        title=_(u"Media URL"),
        required=True
    )

    maxwidth = schema.Int(
        title=_(u"Maximum width"),
        required=False
    )

    maxheight = schema.Int(
        title=_(u"Maximum height"),
        required=False
    )


class EmbedTile(Tile):
    """ A tile that embeds media.
    """

    @ram.cache(lambda method, obj: (obj.data.get('media_url'),
                                    obj.data.get('maxwidth'),
                                    obj.data.get('maxheight')))
    def __call__(self):
        media_url = self.data.get('media_url')
        maxwidth = self.data.get('maxwidth') or None
        maxheight = self.data.get('maxheight') or None

        try:
            response = CONSUMER.embed(
                media_url,
                maxwidth=maxwidth,
                maxheight=maxheight,
            )
            data = response.getData()
        except (oembed.OEmbedError, HTTPError) as e:
            data = {
                "html": "<pre>" + str(e) + "</pre>"
            }

        return u"<html><body>%s</body></html>" % data['html']
