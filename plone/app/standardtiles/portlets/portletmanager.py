# -*- coding: utf-8 -*-
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.portlets.utils import findView
from plone.app.standardtiles.utils import getContentishContext
from plone.portlets.interfaces import IPortletManager
from plone.tiles import Tile
from zope import schema
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface


class IPortletManagerTile(Interface):
    manager = schema.TextLine(
        title=u'Name of the portlet manager to render.',
        required=True
    )

    view = schema.TextLine(
        title=_(u'Name of the view'),
        required=False
    )


@implementer(IPortletManagerTile)
class PortletManagerTile(Tile):
    """A tile that renders a portlet manager."""

    # Needed to support plone.memoize.view.memoize called through findView
    def absolute_url(self):
        return self.url

    def __call__(self):
        """Return the rendered contents of the portlet manager specified."""
        context = getContentishContext(self.context)

        manager = self.data.get('manager')
        viewName = self.data.get('view')
        managerObj = queryUtility(IPortletManager, name=manager)
        if managerObj is None:
            return u'<html><body></body></html>'
        view = findView(self, viewName)

        # set redirection view
        self.request['viewname'] = '@@manage-portlets'
        rendererObj = managerObj(context, self.request, view)
        rendererObj.update()

        return u'<html><body>{0:s}</body></html>'.format(rendererObj.render())
