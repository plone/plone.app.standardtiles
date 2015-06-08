# -*- coding: utf-8 -*-
from plone.app.discussion.browser.comments import CommentForm
from plone.app.layout.globals.interfaces import IViewView
from plone.tiles import Tile
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


class TileCommentForm(CommentForm):
    prefix = 'plone.app.standardtiles.discussion'


class DiscussionTile(Tile):
    """Discussion tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.belowcontent'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.comments'
        )
        if viewlet is not None:
            viewlet.form = TileCommentForm
            viewlet.update()

            # Fix submit redirect from tile to context
            if 'location' in self.request.response.headers:
                self.request.response.redirect(
                    self.request.response.headers['location'].replace(
                        self.url, self.context.absolute_url()))

            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'
