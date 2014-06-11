from zope.interface import Interface

from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IColumn


class IMetadataTile(Interface):
    """Metadata tiles are application tiles that handle metadata
    """

    def get_value(self):
        """Returns the value to display through the template.
        """


class IPortletManager(IPortletManager, IColumn):
    """ a custom portlet manager
    to render single portlets via tiles.
    """


class IPortletManagerAssignment(Interface):
    """ a custom assignment marker interface
    for our portlet manager assignment.
    """
