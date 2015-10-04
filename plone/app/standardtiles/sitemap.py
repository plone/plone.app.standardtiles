# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.navigation import NavigationTile
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from zope import schema
from zope.component import getUtility
from zope.interface import implements

try:
    from Products.CMFPlone.interfaces.controlpanel import INavigationSchema
    HAS_PLONE_5 = True
except ImportError:
    HAS_PLONE_5 = False


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

        if HAS_PLONE_5:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(INavigationSchema,
                                             prefix='plone')
            self.data['bottomLevel'] = settings.sitemap_depth
        else:
            ptool = getToolByName(self.context, 'portal_properties')
            self.data['bottomLevel'] = ptool.navtree_properties.sitemapDepth
