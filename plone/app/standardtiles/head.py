from plone.app.standardtiles.common import ProxyViewletTile
from plone.tiles.tile import Tile
from zope.component import getMultiAdapter


class TitleTile(ProxyViewletTile):
    """A tile rendering the title tag to be inserted in the HTML headers."""

    manager = "plone.htmlhead"
    viewlet = "plone.htmlhead.title"
    section = "head"


class StylesheetsTile(ProxyViewletTile):
    """A stylesheets rendering tile."""

    manager = "plone.htmlhead.links"
    viewlet = "plone.resourceregistries.styles"
    section = "head"


class JavascriptsTile(ProxyViewletTile):
    """A stylesheets rendering tile."""

    manager = "plone.scripts"
    viewlet = "plone.resourceregistries.scripts"
    section = "head"


class FaviconLinkTile(ProxyViewletTile):
    """Favicon link tile implementation."""

    manager = "plone.htmlhead.links"
    viewlet = "plone.links.favicon"
    section = "head"


class AuthorLinkTile(ProxyViewletTile):
    """Author link tile implementation."""

    manager = "plone.htmlhead.links"
    viewlet = "plone.links.author"
    section = "head"


class NavigationLinkTile(Tile):
    """Navigation link tile implementation."""

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        return portal_state.navigation_root_url()


class SearchLinkTile(ProxyViewletTile):
    """Search link tile implementation."""

    manager = "plone.htmlhead.links"
    viewlet = "plone.links.search"
    section = "head"


class RSSLinkTile(ProxyViewletTile):
    """RSS link tile implementation."""

    manager = "plone.htmlhead.links"
    viewlet = "plone.links.RSS"
    section = "head"


class CanonicalUrlTile(ProxyViewletTile):
    """Canonical url tile implementation."""

    manager = "plone.htmlhead.links"
    viewlet = "plone.links.canonical_url"
    section = "head"


class DublinCoreTile(ProxyViewletTile):
    manager = "plone.htmlhead"
    viewlet = "plone.htmlhead.dublincore"
    section = "head"


class SocialTile(ProxyViewletTile):
    manager = "plone.htmlhead"
    viewlet = "plone.htmlhead.socialtags"
    section = "head"
