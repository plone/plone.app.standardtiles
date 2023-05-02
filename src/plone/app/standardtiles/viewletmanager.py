from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.portlets.utils import findView
from plone.tiles import Tile
from zope import schema
from zope.browser.interfaces import IBrowserView
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager

import Acquisition


class IViewletManagerTile(Interface):
    manager = schema.TextLine(title=_("Name of the viewlet manager."), required=True)

    view = schema.TextLine(title=_("Name of the view"), required=False)

    section = schema.Choice(
        title=_("Section of the page"),
        values=("head", "body"),
        required=False,
        default="body",
    )

    viewlet = schema.TextLine(title=_("Name of the viewlet"), required=False)


@implementer(IViewletManagerTile)
class ViewletManagerTile(Tile):
    """A tile that renders a viewlet manager."""

    def __init__(self, context, request):
        # Fix issue where context is a template based view class
        while IBrowserView.providedBy(context) and context is not None:
            context = Acquisition.aq_parent(Acquisition.aq_inner(context))
        super().__init__(context, request)

    # Needed to support plone.memoize.view.memoize called through findView
    def absolute_url(self):
        return self.url

    def __call__(self):
        """Return the rendered contents of the viewlet manager specified."""
        manager = self.data.get("manager")
        viewName = self.data.get("view", None)
        section = self.data.get("section", "body")
        viewlet = self.data.get("viewlet", None)

        view = findView(self, viewName)

        managerObj = queryMultiAdapter(
            (self.context, self.request, view), IViewletManager, name=manager
        )
        managerObj.update()

        obj_to_render = managerObj

        if viewlet:
            provided_viewlets = [i.__name__ for i in managerObj.viewlets]
            if viewlet not in provided_viewlets:
                mgr_name = managerObj.__name__
                msg = f"Viewlet {viewlet} is not provided by {mgr_name}"
                raise ValueError(msg)
            obj_to_render = [i for i in managerObj.viewlets if i.__name__ == viewlet][0]

        if section == "head":
            return "<html><head>%s</head></html>" % obj_to_render.render()
        return "<html><body>%s</body></html>" % obj_to_render.render()
