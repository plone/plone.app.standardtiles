# -*- coding: utf-8 -*-
from plone.app.layout.globals.interfaces import IViewView
from plone.tiles import Tile
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


class KeywordsTile(Tile):
    """A tile that displays the context's keywords, if any."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.belowcontent'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.belowcontenttitle.keywords'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'
