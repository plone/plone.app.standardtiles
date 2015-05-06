# -*- coding: utf-8 -*-
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.navigation import NavigationTile
from plone.supermodel.model import Schema
from zope import schema
from zope.interface import implements


class ISitemapTile(Schema):
    """A tile which can render the sitemap."""
    name = schema.TextLine(
        title=_(u"Title"),
        description=_(u"The title of the sitemap."),
        default=u"",
        required=False
    )


class SitemapTile(NavigationTile):

    implements(ISitemapTile)

    def __init__(self, *arg, **kw):
        super(SitemapTile, self).__init__(*arg, **kw)

        self.data['root'] = None
        self.data['topLevel'] = 0
        self.data['bottomLevel'] = self.properties.sitemapDepth
