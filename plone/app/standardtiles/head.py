# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from cgi import escape
from plone.app.layout.viewlets.interfaces import IHtmlHeadLinks
try:
    from plone.app.layout.viewlets.interfaces import IScripts
except ImportError:
    # BBB for Plone 4
    IScripts = ()
from plone.tiles.tile import Tile
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.viewlet.interfaces import IViewlet


class TitleTile(Tile):
    """A tile rendering the title tag to be inserted in the HTML headers."""

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        page_title = escape(safe_unicode(context_state.object_title()))
        portal_title = escape(safe_unicode(portal_state.portal_title()))
        if page_title == portal_title:
            self.site_title = portal_title
        else:
            self.site_title = u"%s &mdash; %s" % (page_title, portal_title)


@implementer(IHtmlHeadLinks)
class StylesheetsTile(Tile):
    """A stylesheets rendering tile."""

    def __call__(self):
        viewlet = getMultiAdapter(
            (self.context, self.request, self, self),
            IViewlet, name='plone.resourceregistries.styles'
        )
        viewlet.update()
        return u'<html><head>%s</head></html>' % viewlet()


@implementer(IScripts)
class JavascriptsTile(Tile):
    """A javascripts rendering tile."""
    def __call__(self):
        viewlet = getMultiAdapter(
            (self.context, self.request, self, self),
            IViewlet, name='plone.resourceregistries.scripts'
        )
        viewlet.update()
        return u'<html><head>%s</head></html>' % viewlet()


class FaviconLinkTile(Tile):
    """Favicon link tile implementation."""

    @property
    def site_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.portal_url()


class AuthorLinkTile(Tile):
    """Author link tile implementation."""

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.navigation_root_url()

    def show(self):
        tools = getMultiAdapter((self.context, self.request),
                                name='plone_tools')
        properties = tools.properties()
        site_properties = getattr(properties, 'site_properties')
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        anonymous = portal_state.anonymous()
        allowAnonymousViewAbout = site_properties.getProperty(
            'allowAnonymousViewAbout', True)
        return not anonymous or allowAnonymousViewAbout


class NavigationLinkTile(Tile):
    """Navigation link tile implementation."""

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.navigation_root_url()


class SearchLinkTile(Tile):
    """Search link tile implementation."""

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.navigation_root_url()


class RSSLinkTile(Tile):
    """RSS link tile implementation."""

    def allowed(self):
        syntool = getToolByName(self.context, 'portal_syndication')
        try:
            return syntool.isSyndicationAllowed(self.context)
        except TypeError:  # Could not adapt
            return False

    @property
    def url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return '%s/RSS' % context_state.object_url()
