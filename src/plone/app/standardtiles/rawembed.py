from plone.app.standardtiles import _PMF as _
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.supermodel.model import Schema
from plone.tiles import Tile
from plone.tiles.directives import ignore_querystring
from zope import schema
from zope.component import queryUtility


class IRawEmbedTile(Schema):
    """Raw Embed Tile"""

    tile_title = schema.TextLine(
        title=_("Title"),
        description=_(
            """The title will also be used to create
            identifying class on that tile"""
        ),
        required=True,
    )

    show_title = schema.Bool(
        title=_("Show tile title"),
        default=True,
        required=False,
    )

    ignore_querystring("html_snippet")
    html_snippet = schema.SourceText(
        title=_("HTML Snippet"),
        description=_(
            """Be CAREFUL what you paste here, no security
            checks or transforms to safe_html will be done!"""
        ),
        required=False,
    )


class RawEmbedTile(Tile):
    """A tile that embeds media."""

    @property
    def tile_id(self):
        return queryUtility(IIDNormalizer).normalize(self.data.get("tile_title"))

    @property
    def tile_title(self):
        return self.data.get("tile_title")

    @property
    def show_title(self):
        return self.data.get("show_title")

    @property
    def html_snippet(self):
        return self.data.get("html_snippet")
