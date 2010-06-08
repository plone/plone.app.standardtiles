from plone.tiles.tile import Tile
from datetime import date


class FooterTile(Tile):
    """A footer tile
    """

    @property
    def year(self):
        return date.today().year
