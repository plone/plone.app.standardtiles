# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.memoize.view import memoize
from plone.tiles.tile import Tile
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


class BaseViewletTile(Tile):

    manager = None
    viewlet = None

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager,
            name=self.manager
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet,
            name=self.viewlet
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        return u'<html></html>'


class FooterTile(BaseViewletTile):
    """A footer tile."""
    manager = 'plone.portalfooter'
    viewlet = 'plone.footer'


class ColophonTile(BaseViewletTile):
    """A colophon tile."""
    manager = 'plone.portalfooter'
    viewlet = 'plone.colophon'


class SiteActionsTile(BaseViewletTile):
    """A site actions tile."""
    manager = 'plone.portalfooter'
    viewlet = 'plone.site_actions'


class AnalyticsTile(BaseViewletTile):
    """A analytics tile."""
    manager = 'plone.portalfooter'
    viewlet = 'plone.analytics'


class SkipLinksTile(BaseViewletTile):
    """A skip links tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.skip_links'


class LoginTile(Tile):
    """Login tile."""

    def __call__(self):
        context = aq_inner(self.context)
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


class PersonalBarTile(BaseViewletTile):
    """A personal bar tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.personal_bar'


class SearchBoxTile(BaseViewletTile):
    """A search box tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.searchbox'


class AnonToolsTile(BaseViewletTile):
    """An anon tools tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.anontools'


class LogoTile(BaseViewletTile):
    """A logo tile."""
    manager = 'plone.portalheader'
    viewlet = 'plone.logo'


class GlobalSectionsTile(BaseViewletTile):
    """A global sections tile."""
    manager = 'plone.mainnavigation'
    viewlet = 'plone.global_sections'


class PathBarTile(BaseViewletTile):
    """A path bar tile."""
    manager = 'plone.abovecontent'
    viewlet = 'plone.path_bar'


class ToolbarTile(Tile):
    """A Plone 5 toolbar tile."""

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            return u'<html></html>'

        toolbar = getMultiAdapter((self.context, self.request),
                                  name=u'render-toolbar')
        alsoProvides(toolbar, IViewView)
        return u'<html><body>%s</body></html>' % toolbar()


class GlobalStatusMessageTile(BaseViewletTile):
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


class LockInfoTile(BaseViewletTile):
    """A lockinfo tile."""
    manager = 'plone.abovecontent'
    viewlet = 'plone.lockinfo'


class NextPreviousTile(Tile):
    """Tile for showing the next / previous links, based on nextprevious
    viewlets in p.a.layout.
    """

    def __call__(self):
        alsoProvides(self, IViewView)
        links_manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.htmlhead.links'
        )
        links_viewlet = queryMultiAdapter(
            (self.context, self.request, self, links_manager),
            IViewlet, name='plone.nextprevious.links'
        )
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.belowcontent'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.nextprevious'
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


class KeywordsTile(BaseViewletTile):
    """A tile that displays the context's keywords, if any."""
    manager = 'plone.belowcontent'
    viewlet = 'plone.belowcontenttitle.keywords'


class TableOfContentsTile(BaseViewletTile):
    """A Table of contents tile."""
    manager = 'plone.abovecontentbody'
    viewlet = 'plone.tableofcontents'


class DocumentActionsTile(BaseViewletTile):
    """Shows the document actions."""
    manager = 'plone.belowcontentbody'
    viewlet = 'plone.abovecontenttitle.documentactions'


class RelatedItemsTile(BaseViewletTile):
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


class LanguageSelectorTile(Tile):
    """Shows the language selector."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalheader'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.app.multilingual.languageselector'
        )
        # BBB: Plone 4 or no plone.app.multilingual
        if viewlet is None:
            viewlet = queryMultiAdapter(
                (self.context, self.request, self, manager),
                IViewlet, name='plone.app.i18n.locales.languageselector'
            )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        return u'<html></html>'
