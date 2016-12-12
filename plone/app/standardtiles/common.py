# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl.ZopeGuards import guarded_hasattr
from Acquisition import aq_inner
from Acquisition.interfaces import IAcquirer
from DateTime.DateTime import DateTime
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.app.standardtiles.utils import getContentishContext
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.memoize.view import memoize
from plone.tiles.tile import Tile
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.security import checkPermission
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager

import logging


logger = logging.getLogger(__name__)


class BaseViewletTile(Tile):

    def __init__(self, *args, **kwargs):
        super(BaseViewletTile, self).__init__(*args, **kwargs)
        self.context = getContentishContext(self.context)

    def get_viewlet(self, manager_name, viewlet_name):
        # check visibility
        storage = queryUtility(IViewletSettingsStorage)
        if storage is None:
            return None

        skinname = self.context.getCurrentSkinName()

        hidden = frozenset(storage.getHidden(manager_name, skinname))
        if viewlet_name in hidden:
            return None

        # get viewlet instance
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager,
            name=manager_name
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet,
            name=viewlet_name
        )
        if viewlet is None:
            logger.debug(
                'Viewlet tile {0} in manager {1}. '
                'Was not found.'.format(viewlet_name, manager_name)
            )
            return None

        # check permissions - same as in plone.app.viewletmanager
        if IAcquirer.providedBy(viewlet):
            viewlet = viewlet.__of__(viewlet.context)
        if not guarded_hasattr(viewlet, 'render'):
            logger.warn(
                'Blocked attempt to render tile {0} in manager {1}. '
                'Permission denied.'.format(viewlet_name, manager_name)
            )
            return None

        return viewlet


class ProxyViewletTile(BaseViewletTile):

    section = u'body'
    manager = None
    viewlet = None

    def __call__(self):
        alsoProvides(self, IViewView)
        viewlet = self.get_viewlet(self.manager, self.viewlet)
        if viewlet is None:
            return u'<html></html>'

        viewlet.update()
        return u'<html><{section}>{rendered}</{section}></html>'.format(
            rendered=viewlet.render(),
            section=self.section
        )


class FooterTile(ProxyViewletTile):
    """A footer tile."""
    manager = 'plone.portalfooter'
    viewlet = 'plone.footer'


class ColophonTile(ProxyViewletTile):
    """A colophon tile."""
    manager = 'plone.portalfooter'
    viewlet = 'plone.colophon'


class SiteActionsTile(ProxyViewletTile):
    """A site actions tile."""
    manager = 'plone.portalfooter'
    viewlet = 'plone.site_actions'


class AnalyticsTile(ProxyViewletTile):
    """A analytics tile."""
    manager = 'plone.portalfooter'
    viewlet = 'plone.analytics'


class LoginTile(Tile):
    """Login tile."""

    def __call__(self):
        context = getContentishContext(self.context)
        request = self.request
        self.membership = getToolByName(context, 'portal_membership')
        self.context_state = getMultiAdapter((context, request),
                                             name=u'plone_context_state')
        self.portal_state = getMultiAdapter((context, request),
                                            name=u'plone_portal_state')
        self.pas_info = getMultiAdapter((context, request), name=u'pas_info')
        self.navigation_root_url = self.portal_state.navigation_root_url()

        self.update()
        return self.index()

    def show(self):
        if not self.portal_state.anonymous():
            return False
        if not self.pas_info.hasLoginPasswordExtractor():
            return False
        page = self.request.get('URL', '').split('/')[-1]
        return page not in ('login_form', '@@register')

    @property
    def available(self):
        return self.auth() is not None and self.show()

    def login_form(self):
        return '%s/login_form' % self.portal_state.portal_url()

    def mail_password_form(self):
        return '%s/mail_password_form' % self.portal_state.portal_url()

    def login_name(self):
        auth = self.auth()
        name = None
        if auth is not None:
            name = getattr(auth, 'name_cookie', None)
        if not name:
            name = '__ac_name'
        return name

    def login_password(self):
        auth = self.auth()
        passwd = None
        if auth is not None:
            passwd = getattr(auth, 'pw_cookie', None)
        if not passwd:
            passwd = '__ac_password'
        return passwd

    def join_action(self):
        context = self.context
        tool = getToolByName(context, 'portal_actions')
        join = tool.listActionInfos(action_chain='user/join', object=context)
        if len(join) > 0:
            return join[0]['url']
        return None

    def can_register(self):
        if getToolByName(self.context, 'portal_registration', None) is None:
            return False
        return self.membership.checkPermission('Add portal member',
                                               self.context)

    def can_request_password(self):
        return self.membership.checkPermission('Mail forgotten password',
                                               self.context)

    @memoize
    def auth(self, _marker=[]):
        acl_users = getToolByName(self.context, 'acl_users')
        return getattr(acl_users, 'credentials_cookie_auth', None)

    def update(self):
        pass


class PersonalBarTile(ProxyViewletTile):
    """A personal bar tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.personal_bar'


class SearchBoxTile(ProxyViewletTile):
    """A search box tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.searchbox'


class AnonToolsTile(ProxyViewletTile):
    """An anon tools tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.anontools'


class LogoTile(ProxyViewletTile):
    """A logo tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.logo'


class GlobalSectionsTile(ProxyViewletTile):
    """A global sections tile."""
    manager = 'plone.mainnavigation'
    viewlet = 'plone.global_sections'


class PathBarTile(ProxyViewletTile):
    """A path bar tile."""
    manager = 'plone.abovecontent'
    viewlet = 'plone.path_bar'


class ToolbarTile(Tile):
    """A Plone 5 toolbar tile."""

    def __call__(self):
        context = getContentishContext(self.context)

        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            return u'<html></html>'

        toolbar = getMultiAdapter((context, self.request),
                                  name=u'render-toolbar')
        alsoProvides(toolbar, IViewView)
        return u'<html><body>%s</body></html>' % toolbar()


class GlobalStatusMessageTile(ProxyViewletTile):
    """Display messages to the current user"""
    manager = 'plone.globalstatusmessage'
    viewlet = 'plone.globalstatusmessage'


class DocumentBylineTile(Tile):
    """A document byline tile."""

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.anonymous = self.portal_state.anonymous()

    def show(self):
        properties = getToolByName(self.context, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        allowAnonymousViewAbout = site_properties.getProperty(
            'allowAnonymousViewAbout', True)
        return not self.anonymous or allowAnonymousViewAbout

    def show_history(self):
        if not _checkPermission(
            'CMFEditions: Access previous versions',
            self.context
        ):
            return False
        if IViewView.providedBy(self.__parent__):
            return True
        if IFolderContentsView.providedBy(self.__parent__):
            return True
        return False

    def locked_icon(self):
        if not getSecurityManager().checkPermission('Modify portal content',
                                                    self.context):
            return ""

        locked = False
        lock_info = queryMultiAdapter((self.context, self.request),
                                      name='plone_lock_info')
        if lock_info is not None:
            locked = lock_info.is_locked()
        else:
            context = aq_inner(self.context)
            is_locked = getattr(context.aq_explicit, 'wl_isLocked', None)
            lockable = is_locked is not None
            locked = lockable and context.wl_isLocked()

        if not locked:
            return ""

        portal = self.portal_state.portal()
        icon = portal.restrictedTraverse('lock_icon.png')
        return icon.tag(title='Locked')

    def creator(self):
        return self.context.Creator()

    def author(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.getMemberInfo(self.creator())

    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()

    def isExpired(self):
        if base_hasattr(self.context, 'expires'):
            return self.context.expires().isPast()
        return False

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                    domain='plonelocales')

    def pub_date(self):
        """Return object effective date.

        Return None if publication date is switched off in global site settings
        or if Effective Date is not set on object.
        """
        # check if we are allowed to display publication date
        properties = getToolByName(self.context, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        if not site_properties.getProperty('displayPublicationDateInByline',
           False):
            return None

        # check if we have Effective Date set
        date = self.context.EffectiveDate()
        if not date or date == 'None':
            return None

        return DateTime(date)


class LockInfoTile(ProxyViewletTile):
    """A lockinfo tile."""
    manager = 'plone.abovecontent'
    viewlet = 'plone.lockinfo'

    def __call__(self):
        if checkPermission('cmf.ModifyPortalContent', self.context):
            return super(LockInfoTile, self).__call__()
        else:
            return u'<html></html>'


class NextPreviousTile(BaseViewletTile):
    """Tile for showing the next / previous links, based on nextprevious
    viewlets in p.a.layout.
    """

    def __call__(self):
        alsoProvides(self, IViewView)
        links_viewlet = self.get_viewlet(
            'plone.htmlhead.links',
            'plone.nextprevious.links'
        )
        viewlet = self.get_viewlet(
            'plone.belowcontent',
            'plone.nextprevious'
        )
        if links_viewlet and viewlet:
            links_viewlet.update()
            viewlet.update()
            try:
                # XXX: We need to cheat viewlet.isViewTemplate:
                url = self.request.get('ACTUAL_URL')
                self.request.set('ACTUAL_URL', self.context.absolute_url())
                return u'<html><head>%s</head><body>%s</body></html>' % (
                    links_viewlet.render(), viewlet.render())
            finally:
                self.request.set('ACTUAL_URL', url)
        else:
            return u'<html></html>'


class KeywordsTile(ProxyViewletTile):
    """A tile that displays the context's keywords, if any."""
    manager = 'plone.belowcontent'
    viewlet = 'plone.belowcontenttitle.keywords'


class TableOfContentsTile(ProxyViewletTile):
    """A Table of contents tile."""
    manager = 'plone.abovecontentbody'
    viewlet = 'plone.tableofcontents'


class DocumentActionsTile(ProxyViewletTile):
    """Shows the document actions."""
    manager = 'plone.belowcontentbody'
    viewlet = 'plone.abovecontenttitle.documentactions'


class RelatedItemsTile(ProxyViewletTile):
    """A related items tile."""
    manager = 'plone.belowcontentbody'
    viewlet = 'plone.belowcontentbody.relateditems'


class HistoryTile(Tile):
    """Provides the history as tile. Basically just renders
    the @@contenthistorypopup view, which includes version / content
    history and workflow history.
    """

    def __call__(self):
        return self.context.restrictedTraverse('@@contenthistorypopup')()


class LanguageSelectorTile(ProxyViewletTile):
    """Shows the language selector."""

    manager = 'plone.portalheader'
    viewlet = 'plone.app.multilingual.languageselector'
