from Products.statusmessages.interfaces import IStatusMessage
from plone.app.layout.globals.interfaces import IViewView
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.interfaces import IViewlet

from plone.tiles import Tile


class PersonalBarTile(Tile):
    """A personal bar tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalheader'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.personal_bar'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class GlobalSectionsTile(Tile):
    """A global sections tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalheader'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.global_sections'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class GlobalStatusMessageTile(Tile):
    """Display messages to the current user"""

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        if not self.request.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            self.status = IStatusMessage(self.request)
            self.messages = self.status.show()
        else:
            return u'<html></html>'


class EditBarTile(Tile):
    """A edit bar tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.contentviews'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.contentviews'
        )
        actions_viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.contentactions'
        )
        if viewlet is not None and actions_viewlet is not None:
            viewlet.update()
            actions_viewlet.update()
            return (u'<html><body><div id="edit-bar">'
                    u'%s%s</div></body></html>') % (
                       viewlet.render(), actions_viewlet.render()
                   )
        else:
            return u'<html></html>'


class DocumentBylineTile(Tile):
    """A document byline tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.belowcontenttitle'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.belowcontenttitle.documentbyline'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'
