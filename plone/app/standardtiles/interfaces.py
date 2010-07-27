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

    images_repo_path = schema.TextLine(title=u"Images repository path",
                                      description=u"The relative path to the folder containing the images available to select in the image tile, starting from the root of the site.",
                                      default=u"images")
