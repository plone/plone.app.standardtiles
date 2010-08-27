from zope.interface import Interface
from zope import schema


class IMetadataTile(Interface):
    """Metadata tiles are application tiles that handle metadata
    """

    def get_value(self):
        """Returns the value to display through the template.
        """

class IStandardTilesSettings(Interface):
    """Settings for standard tiles."""
    listing_views = schema.Dict(title=u"Listing views",
                                description=u"Listing views available for the content listing tile",
                                key_type=schema.TextLine(),
                                value_type=schema.TextLine())

    images_repo_path = schema.TextLine(title=u"Images repository path",
                                      description=u"The relative path to the folder containing the images available to select in the image tile, starting from the root of the site.",
                                      default=u"images")
