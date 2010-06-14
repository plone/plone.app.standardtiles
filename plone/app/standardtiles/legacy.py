from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.component import getUtility 
from zope.interface import Interface
from zope import schema

from plone.tiles import Tile

from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager


class IViewletManagerTile(Interface):
    manager = schema.TextLine(title=u"Name of the viewlet manager to render.",
                           required=True)


class ViewletManagerTile(Tile):
    """A tile that renders a viewlet manager."""

    implements(IViewletManagerTile)

    def __call__(self):
        """Return the rendered contents of the viewlet manager specified."""
        manager = self.data.get('manager')
        managerObj = queryMultiAdapter((self.context, self.request, self), IViewletManager, manager)
        managerObj.update()
        return "<html><body>%s</body></html>" % managerObj.render()


class IPortletManagerTile(Interface):
    manager = schema.TextLine(title=u"Name of the portlet manager to render.",
                           required=True)


class PortletManagerTile(Tile):
    """A tile that renders a portlet manager."""

    implements(IPortletManagerTile)

    def __call__(self):
        """Return the rendered contents of the portlet manager specified."""
        manager = self.data.get('manager')
        managerObj = getUtility(IPortletManager, name=manager)
        rendererObj = managerObj(self.context, self.request, self)
        rendererObj.update()
        return "<html><body>%s</body></html>" % rendererObj.render()
