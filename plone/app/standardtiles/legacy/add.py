#-*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.portlets.browser.adding import PortletAdding as BasePortletAdding
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.tiles import MessageFactory as _
from plone.app.tiles.browser.add import DefaultAddForm
from plone.app.tiles.browser.add import DefaultAddView
from plone.portlets.utils import hashPortletInfo
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUIDGenerator
from z3c.form import button
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.traversing.browser.absoluteurl import absoluteURL

try:
    from plone.protect.utils import addTokenToUrl
    HAS_PLONE_PROTECT = True
except ImportError:
    HAS_PLONE_PROTECT = False


class PortletAdding(BasePortletAdding):
    """Overrides portlet manager '+' view in order to get the hash of the
    portlet after creation and make the form redirect to the tile URL.
    """

    def add(self, content):
        """Add the rule to the context."""
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


class PortletTileAddForm(DefaultAddForm):

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        mgr_name = 'plone.app.standardtiles.portletManager'
        add_portlet_url = '/'.join([
            self.context.absolute_url(),
            '++contextportlets++{0}/+'.format(mgr_name),
            data['portlet_type']
        ])
        if HAS_PLONE_PROTECT:
            add_portlet_url = addTokenToUrl(add_portlet_url, self.request)
        self.request.response.redirect(add_portlet_url)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        # TODO
        tileDataJson = {}
        tileDataJson['action'] = "cancel"
        url = self.request.getURL()
        self.request.response.redirect(url)


class PortletTileAddView(DefaultAddView):
    form = PortletTileAddForm
