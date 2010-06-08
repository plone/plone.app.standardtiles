from plone.tiles.tile import Tile
from datetime import date
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode


class FooterTile(Tile):
    """A footer tile
    """

    @property
    def year(self):
        return date.today().year


class SiteActionsTile(Tile):
    """A site actions tile
    """

    def site_actions(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.actions('site_actions')


class AnalyticsTile(Tile):
    """A analytics tile
    """

    def __call__(self):
        ptool = getToolByName(self.context, "portal_properties")
        snippet = safe_unicode(ptool.site_properties.webstats_js)
        return "<html><body>%s</body></html>" % snippet


class SkipLinksTile(Tile):
    """A skip links tile
    """

    @property
    def current_page_url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.current_page_url
