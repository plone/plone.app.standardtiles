from plone.app.standardtiles.interfaces import IMetadataTile
from plone.tiles.tile import Tile
from zope.interface import implementer


@implementer(IMetadataTile)
class BaseMetadataTile(Tile):
    """The base class for metadata tiles (such as title and description)."""

    def get_value(self):
        return ""

    @property
    def value(self):
        return self.get_value()


class DefaultTitleTile(BaseMetadataTile):
    """A default tile for title."""

    def get_value(self):
        return "Insert the content title here"


class DefaultDescriptionTile(BaseMetadataTile):
    """A default tile for description."""

    def get_value(self):
        return "Insert the content description here"


class DublinCoreTitleTile(BaseMetadataTile):
    """A tile for dublin core content title."""

    def get_value(self):
        return self.context.Title()


class DublinCoreDescriptionTile(BaseMetadataTile):
    """A tile for dublin core content description."""

    def get_value(self):
        return self.context.Description()


class DexterityTitleTile(BaseMetadataTile):
    """A tile for dexterity content title."""

    def get_value(self):
        return self.context.title


class DexterityDescriptionTile(BaseMetadataTile):
    """A tile for dexterity content description."""

    def get_value(self):
        return self.context.description
