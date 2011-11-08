from zope.interface import Interface
from zope import schema

from plone.app.standardtiles import PloneMessageFactory as _


class IMetadataTile(Interface):
    """Metadata tiles are application tiles that handle metadata
    """

    def get_value(self):
        """Returns the value to display through the template.
        """


class IStandardTilesSettings(Interface):
    """Settings for standard tiles."""

    images_repo_path = schema.TextLine(title=_(u"Images repository path"),
                                       description=_(u"The relative path to "
                                                      "the folder containing "
                                                      "the images available "
                                                      "to select in the image "
                                                      "tile, starting from "
                                                      "the root of the site."),
                                       default=_(u"images"))
