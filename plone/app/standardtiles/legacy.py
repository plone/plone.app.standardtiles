from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.interface import Interface
from zope import schema

from plone.tiles import Tile

from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager

from plone.app.standardtiles import PloneMessageFactory as _


class IViewletManagerTile(Interface):
    manager = schema.TextLine(title=_(u"Name of the viewlet manager."),
                              required=True)
    
    view = schema.TextLine(title=_(u"Name of the view"),
                               required=False)
    
    section = schema.Choice(title=_(u"Section of the page"),
                            values=(u"head", "body"),
                            required=False,
                            default="body")

class ViewletManagerTile(Tile):
    """A tile that renders a viewlet manager."""

    implements(IViewletManagerTile)

    def __call__(self):
        """Return the rendered contents of the viewlet manager specified."""
        manager = self.data.get('manager')
        viewName = self.data.get('view', None)
        section = self.data.get('section', 'body')
        
        view = self
        if viewName is not None:
            view = queryMultiAdapter((self.context, self.request),
                                     name=viewName)
            if view is None:
                return u""
        
        managerObj = queryMultiAdapter((self.context, self.request, view),
                                       IViewletManager, name=manager)
        managerObj.update()
        
        if section == 'head':
            return u"<html><head>%s</head></html>" % managerObj.render()
        else:
            return u"<html><body>%s</body></html>" % managerObj.render()


class IPortletManagerTile(Interface):
    manager = schema.TextLine(title=u"Name of the portlet manager to render.",
                           required=True)
    
    view = schema.TextLine(title=_(u"Name of the view"),
                               required=False)

class PortletManagerTile(Tile):
    """A tile that renders a portlet manager."""

    implements(IPortletManagerTile)

    def __call__(self):
        """Return the rendered contents of the portlet manager specified."""
        manager = self.data.get('manager')
        viewName = self.data.get('view')
        
        managerObj = getUtility(IPortletManager, name=manager)
        
        view = self
        if viewName is not None:
            view = queryMultiAdapter((self.context, self.request),
                                     name=viewName)
            if view is None:
                return u""
        
        rendererObj = managerObj(self.context, self.request, view)
        rendererObj.update()
        return u"<html><body>%s</body></html>" % rendererObj.render()
