from plone.tiles.tile import Tile
from datetime import date
from zope.component import getMultiAdapter


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
