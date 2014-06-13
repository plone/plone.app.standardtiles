#-*- coding: utf-8 -*-

from zope.browser.interfaces import IView
from zope.component import queryMultiAdapter


def findView(tile, viewName):
    """Find the view to use for portlet/viewlet context lookup."""

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
