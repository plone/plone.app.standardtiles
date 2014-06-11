from zope.interface import Interface
from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.browser.interfaces import IView

from zope import schema

from plone.tiles import Tile

from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager

from plone.app.standardtiles import PloneMessageFactory as _

def findView(tile, viewName):
    """Find the view to use for portlet/viewlet context lookup
    """

    view = tile
    prequest = tile.request.get('PARENT_REQUEST', None)

    # Attempt to determine the underlying view name from the parent request
    # XXX: This won't work if using ESI rendering or any other
    # technique that doesn't use plone.subrequest
    if viewName is None and prequest is not None:
        ppublished = prequest.get('PUBLISHED', None)
        if IView.providedBy(ppublished):
            viewName = prequest['PUBLISHED'].__name__

    context = tile.context
    request = tile.request
    if prequest is not None:
        request = prequest

    if viewName is not None:
        view = queryMultiAdapter((context, request), name=viewName)

    if view is None:
        view = tile

    # Decide whether to mark the view
    # XXX: Again, this probably won't work well if not using plone.subrequest
    layoutPolicy = queryMultiAdapter((context, request), name='plone_layout')
    if layoutPolicy is not None:
        layoutPolicy.mark_view(view)

    return view

class IViewletManagerTile(Interface):
    manager = schema.TextLine(title=_(u"Name of the viewlet manager."),
                              required=True)

    view = schema.TextLine(title=_(u"Name of the view"),
                               required=False)

    section = schema.Choice(title=_(u"Section of the page"),
                            values=(u"head", "body"),
                            required=False,
                            default="body")

    viewlet = schema.TextLine(title=_(u"Name of the viewlet"),
                               required=False)

class ViewletManagerTile(Tile):
    """A tile that renders a viewlet manager."""

    implements(IViewletManagerTile)

    def __call__(self):
        """Return the rendered contents of the viewlet manager specified."""
        manager = self.data.get('manager')
        viewName = self.data.get('view', None)
        section = self.data.get('section', 'body')
        viewlet = self.data.get('viewlet', None)

        view = findView(self, viewName)

        managerObj = queryMultiAdapter((self.context, self.request, view), IViewletManager, name=manager)
        managerObj.update()

        obj_to_render = managerObj

        if viewlet:
            provided_viewlets = [i.__name__ for i in managerObj.viewlets]
            if viewlet not in provided_viewlets:
                raise ValueError('Viewlet %s is not provided by %s' % (viewlet, managerObj.__name__))
            obj_to_render = [i for i in managerObj.viewlets if i.__name__ == viewlet][0]

        if section == 'head':
            return u"<html><head>%s</head></html>" % obj_to_render.render()
        else:
            return u"<html><body>%s</body></html>" % obj_to_render.render()


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

        view = findView(self, viewName)

        rendererObj = managerObj(self.context, self.request, view)
        rendererObj.update()
        return u"<html><body>%s</body></html>" % rendererObj.render()
