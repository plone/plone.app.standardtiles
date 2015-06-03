#-*- coding: utf-8 -*-
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.portlets.utils import findView
from plone.tiles import Tile
from zope import schema
from zope.interface import Interface
from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager


class IViewletManagerTile(Interface):

    manager = schema.TextLine(
        title=_(u"Name of the viewlet manager."),
        required=True
    )

    view = schema.TextLine(
        title=_(u"Name of the view"),
        required=False
    )

    section = schema.Choice(
        title=_(u"Section of the page"),
        values=(u"head", "body"),
        required=False,
        default="body"
    )

    viewlet = schema.TextLine(
        title=_(u"Name of the viewlet"),
        required=False
    )


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

        managerObj = queryMultiAdapter(
            (self.context, self.request, view),
            IViewletManager,
            name=manager
        )
        managerObj.update()

        obj_to_render = managerObj

        if viewlet:
            provided_viewlets = [i.__name__ for i in managerObj.viewlets]
            if viewlet not in provided_viewlets:
                mgr_name = managerObj.__name__
                msg = 'Viewlet %s is not provided by %s' % (viewlet,
                                                            mgr_name)
                raise ValueError(msg)
            obj_to_render = [i for i in managerObj.viewlets
                             if i.__name__ == viewlet][0]

        if section == 'head':
            return u"<html><head>%s</head></html>" % obj_to_render.render()
        else:
            return u"<html><body>%s</body></html>" % obj_to_render.render()

