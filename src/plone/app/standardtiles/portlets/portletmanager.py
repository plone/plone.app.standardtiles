from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.portlets.utils import findView
from plone.portlets.interfaces import IPortletManager
from plone.tiles import Tile
from zope import schema
from zope.browser.interfaces import IBrowserView
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface

import Acquisition


class IPortletManagerTile(Interface):
    manager = schema.TextLine(
        title="Name of the portlet manager to render.", required=True
    )

    view = schema.TextLine(title=_("Name of the view"), required=False)


@implementer(IPortletManagerTile)
class PortletManagerTile(Tile):
    """A tile that renders a portlet manager."""

    def __init__(self, context, request):
        # Fix issue where context is a template based view class
        while IBrowserView.providedBy(context) and context is not None:
            context = Acquisition.aq_parent(Acquisition.aq_inner(context))
        super().__init__(context, request)

    # Needed to support plone.memoize.view.memoize called through findView
    def absolute_url(self):
        return self.url

    def __call__(self):
        """Return the rendered contents of the portlet manager specified."""
        manager = self.data.get("manager")
        viewName = self.data.get("view")
        managerObj = queryUtility(IPortletManager, name=manager)
        if managerObj is None:
            return "<html><body></body></html>"
        view = findView(self, viewName)

        # set redirection view
        self.request["viewname"] = "@@manage-portlets"
        rendererObj = managerObj(self.context, self.request, view)
        rendererObj.update()

        return f"<html><body>{rendererObj.render():s}</body></html>"
