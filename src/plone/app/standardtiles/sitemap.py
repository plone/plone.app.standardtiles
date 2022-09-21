from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.navigation import NavigationTile
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from Products.CMFPlone.interfaces.controlpanel import INavigationSchema
from zope import schema
from zope.component import getUtility
from zope.interface import implementer


class ISitemapTile(Schema):
    """A tile which can render the sitemap."""

    name = schema.TextLine(
        title=_("Title"),
        description=_("The title of the sitemap."),
        default="",
        required=False,
    )


@implementer(ISitemapTile)
class SitemapTile(NavigationTile):
    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self.data["root"] = None
        self.data["topLevel"] = 0

        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        self.data["bottomLevel"] = settings.sitemap_depth
