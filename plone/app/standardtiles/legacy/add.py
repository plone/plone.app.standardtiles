#-*- coding: utf-8 -*-

from zope.lifecycleevent import ObjectAddedEvent
from zope.component import getUtility
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.lifecycleevent import ObjectCreatedEvent
from zope.event import notify

from plone.uuid.interfaces import IUUIDGenerator
from plone.tiles.interfaces import ITileDataManager


from zope.container.interfaces import INameChooser

from Acquisition import aq_inner
from Acquisition import aq_base
from Acquisition import aq_parent

from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.browser.adding import PortletAdding as BasePortletAdding
from plone.portlets.utils import hashPortletInfo


class PortletAdding(BasePortletAdding):
    """ overrides portlet manager '+' view
    in order to get the hash of the portlet
    after creation and make the form redirect
    to the tile URL.
    """

    def add(self, content):
        """Add the rule to the context
        """
        context = aq_inner(self.context)
        manager = aq_base(context)

        IPortletPermissionChecker(context)()

        portlet_name = INameChooser(manager).chooseName(None, content)
        manager[portlet_name] = content

        # our category is always 'context'
        # we need the key but we do not know how to get it
        # from the assignment or the manager
        content_object = aq_parent(aq_inner(self.context))
        key = '/'.join(content_object.getPhysicalPath())
        info = {
            'manager': manager.__manager__,
            'category': manager.__category__,
            'key': key,
            'name': portlet_name,
        }
        portlet_hash = hashPortletInfo(info)
        tile_url = add_tile(content_object,
                            self.request,
                            portlet_hash)
        # we need to set the referer in the request form
        # to get proper redirect
        self.request.form['referer'] = tile_url

    def nextURL(self):
        # this is not used at all
        pass


def add_tile(context, request, portlet_hash):
    data = {
        'portlet_hash': portlet_hash,
    }
    generator = getUtility(IUUIDGenerator)
    tileId = generator()

    # Traverse to a new tile in the context, with no data
    typeName = 'plone.app.standardtiles.portlet'
    tile = context.restrictedTraverse('@@%s/%s' % (typeName, tileId,))

    dataManager = ITileDataManager(tile)
    dataManager.set(data)

    # Look up the URL - we need to do this after we've set the data to
    # correctly account for transient tiles
    tileURL = absoluteURL(tile, request)

    notify(ObjectCreatedEvent(tile))
    notify(ObjectAddedEvent(tile, context, tileId))

    return tileURL
