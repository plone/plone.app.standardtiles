# -*- coding: utf-8 -*-
from plone.app.portlets.interfaces import IColumn
from plone.portlets.interfaces import IPortletManager
from zope.interface import Interface


class IMetadataTile(Interface):
    """Metadata tiles are application tiles that handle metadata."""

    def get_value(self):
        """Returns the value to display through the template."""


class IPortletManager(IPortletManager, IColumn):
    """A custom portlet manager to render single portlets via tiles."""


class IPortletManagerAssignment(Interface):
    """A custom assignment marker interface for our portlet manager assignment.
    """
