# -*- coding: utf-8 -*-
from plone.tiles.tile import Tile
from zope.component import getMultiAdapter
from plone.app.standardtiles.common import BaseViewletTile


class TitleTile(BaseViewletTile):
    """A tile rendering the title tag to be inserted in the HTML headers."""
    manager = 'plone.htmlhead'
    viewlet = 'plone.htmlhead.title'
    section = u'head'


class StylesheetsTile(BaseViewletTile):
    """A stylesheets rendering tile."""
    manager = 'plone.htmlhead.links'
    viewlet = 'plone.resourceregistries.styles'
    section = u'head'


class JavascriptsTile(BaseViewletTile):
    """A stylesheets rendering tile."""
    manager = 'plone.scripts'
    viewlet = 'plone.resourceregistries.scripts'
    section = u'head'


class FaviconLinkTile(BaseViewletTile):
    """Favicon link tile implementation."""
    manager = 'plone.htmlhead.links'
    viewlet = 'plone.links.favicon'
    section = u'head'


class AuthorLinkTile(BaseViewletTile):
    """Author link tile implementation."""
    manager = 'plone.htmlhead.links'
    viewlet = 'plone.links.author'
    section = u'head'


class NavigationLinkTile(Tile):
    """Navigation link tile implementation."""

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.navigation_root_url()


class SearchLinkTile(BaseViewletTile):
    """Search link tile implementation."""
    manager = 'plone.htmlhead.links'
    viewlet = 'plone.links.search'
    section = u'head'


class RSSLinkTile(BaseViewletTile):
    """RSS link tile implementation."""
    manager = 'plone.htmlhead.links'
    viewlet = 'plone.links.RSS'
    section = u'head'


class CanonicalUrlTile(BaseViewletTile):
    """Canonical url tile implementation."""
    manager = 'plone.htmlhead.links'
    viewlet = 'plone.links.canonical_url'
    section = u'head'


class DublinCoreTile(BaseViewletTile):
    manager = 'plone.htmlhead'
    viewlet = 'plone.htmlhead.dublincore'
    section = u'head'


class SocialTile(BaseViewletTile):
    manager = 'plone.htmlhead'
    viewlet = 'plone.htmlhead.socialtags'
    section = u'head'
