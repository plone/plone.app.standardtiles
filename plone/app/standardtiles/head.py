# -*- coding: utf-8 -*-
from plone.app.layout.globals.interfaces import IViewView
from plone.tiles.tile import Tile
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


class TitleTile(Tile):
    """A tile rendering the title tag to be inserted in the HTML headers."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.htmlhead.title'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class StylesheetsTile(Tile):
    """A stylesheets rendering tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead.links'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.resourceregistries.styles'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class JavascriptsTile(Tile):
    """A javascripts rendering tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.scripts'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.resourceregistries.scripts'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class FaviconLinkTile(Tile):
    """Favicon link tile implementation."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead.links'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.links.favicon'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class AuthorLinkTile(Tile):
    """Author link tile implementation."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead.links'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.links.author'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class NavigationLinkTile(Tile):
    """Navigation link tile implementation."""

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.navigation_root_url()


class SearchLinkTile(Tile):
    """Search link tile implementation."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead.links'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.links.search'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class RSSLinkTile(Tile):
    """RSS link tile implementation."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead.links'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.links.RSS'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class CanonicalUrlTile(Tile):
    """Canonical url tile implementation."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead.links'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.links.canonical_url'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class DublinCoreTile(Tile):
    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.htmlhead.dublincore'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'


class SocialTile(Tile):
    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.htmlhead.socialtags'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><head>%s</head></html>' % viewlet.render()
        else:
            return u'<html></html>'
