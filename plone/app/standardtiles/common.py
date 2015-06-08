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


class FooterTile(Tile):
    """A footer tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalfooter'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.footer'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class ColophonTile(Tile):
    """A colophon tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalfooter'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.colophon'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class SiteActionsTile(Tile):
    """A site actions tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalfooter'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.site_actions'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class AnalyticsTile(Tile):
    """A analytics tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalfooter'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.analytics'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class SkipLinksTile(Tile):
    """A skip links tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalheader'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.skip_links'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


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


class PersonalBarTile(Tile):
    """A personal bar tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.toolbar'
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


class SearchBoxTile(Tile):
    """A search box tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalheader'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.searchbox'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class AnonToolsTile(Tile):
    """An anon tools tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalheader'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.anontools'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class LogoTile(Tile):
    """A logo tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.portalheader'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.logo'
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
            IViewletManager, name='plone.mainnavigation'
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


class PathBarTile(Tile):
    """A path bar tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.abovecontent'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.path_bar'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


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


class GlobalStatusMessageTile(Tile):
    """Display messages to the current user"""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.globalstatusmessage'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.globalstatusmessage'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


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
        if not _checkPermission('CMFEditions: Access previous versions', self.context):
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
            lockable = getattr(context.aq_explicit, 'wl_isLocked', None) is not None
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

    def toLocalizedTime(self, time, long_format=None, time_only = None):
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


class LockInfoTile(Tile):
    """A lockinfo tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.abovecontent'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.lockinfo'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


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


class DocumentActionsTile(Tile):
    """Shows the document actions."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.belowcontentbody'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.abovecontenttitle.documentactions'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


class RelatedItemsTile(Tile):
    """A related items tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager, name='plone.belowcontentbody'
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager),
            IViewlet, name='plone.belowcontentbody.relateditems'
        )
        if viewlet is not None:
            viewlet.update()
            return u'<html><body>%s</body></html>' % viewlet.render()
        else:
            return u'<html></html>'


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
        else:
            return u'<html></html>'
