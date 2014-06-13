#-*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface
from zope.interface import implements
from zope.component import getUtility
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.legacy.utils import findView
from plone.portlets.interfaces import IPortletManager
from plone.tiles import Tile


class IPortletManagerTile(Interface):
    manager = schema.TextLine(
        title=u"Name of the portlet manager to render.",
        required=True
    )

    view = schema.TextLine(
        title=_(u"Name of the view"),
        required=False
    )


class PortletManagerTile(Tile):
    """A tile that renders a portlet manager."""

    implements(IPortletManagerTile)

    def __call__(self):
        """Return the rendered contents of the portlet manager specified."""

        manager = self.data.get('manager')
        viewName = self.data.get('view')
        managerObj = getUtility(IPortletManager, name=manager)
        view = findView(self, viewName)

        # set redirection view
        self.request['viewname'] = '@@manage-portlets'
        rendererObj = managerObj(self.context, self.request, view)
        rendererObj.update()

        return u"<html><body>%s</body></html>" % rendererObj.render()
