# -*- coding: utf-8 -*-
from datetime import date
from urllib import unquote

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from plone.locking.interfaces import ITTWLockable
from plone.memoize.view import memoize
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter

from plone.tiles.tile import Tile


class TextTile(Tile):
    """A text tile."""


class FooterTile(Tile):
    """A footer tile."""

    @property
    def year(self):
        return date.today().year


class SiteActionsTile(Tile):
    """A site actions tile."""

    def site_actions(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.actions('site_actions')


class AnalyticsTile(Tile):
    """A analytics tile."""

    def __call__(self):
        ptool = getToolByName(self.context, "portal_properties")
        snippet = safe_unicode(ptool.site_properties.webstats_js)
        return "<html><body>%s</body></html>" % snippet


class SkipLinksTile(Tile):
    """A skip links tile."""

    @property
    def current_page_url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.current_page_url


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
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.navigation_root_url = self.portal_state.navigation_root_url()

        self.update()
        return self.index()

    def update(self):
        context = aq_inner(self.context)

        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')

        sm = getSecurityManager()
        self.user_actions = context_state.actions('user')
        self.anonymous = self.portal_state.anonymous()

        if not self.anonymous:
            member = self.portal_state.member()
            userid = member.getId()

            if sm.checkPermission('Portlets: View dashboard', context):
                self.homelink_url = self.navigation_root_url + '/dashboard'
            else:
                self.homelink_url = self.navigation_root_url + \
                    '/personalize_form'

            membership = getToolByName(context, 'portal_membership')
            member_info = membership.getMemberInfo(member.getId())
            # member_info is None if there's no Plone user object, as when
            # using OpenID.
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                self.user_name = fullname
            else:
                self.user_name = userid


class SearchBoxTile(Tile):
    """A search box tile."""

    def __call__(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.navigation_root_url = self.portal_state.navigation_root_url()

        self.update()
        return self.index()

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        props = getToolByName(self.context, 'portal_properties')
        livesearch = props.site_properties.getProperty('enable_livesearch',
                                                       False)
        if livesearch:
            self.search_input_id = "searchGadget"
        else:
            self.search_input_id = "nolivesearchGadget"  # don't use "" here!

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())


class LogoTile(Tile):
    """A logo tile."""

    def __call__(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.navigation_root_url = self.portal_state.navigation_root_url()

        self.update()
        return self.index()

    def update(self):
        portal = self.portal_state.portal()
        bprops = portal.restrictedTraverse('base_properties', None)
        if bprops is not None:
            logoName = bprops.logoName
        else:
            logoName = 'logo.jpg'
        try:
            self.logo_tag = portal.restrictedTraverse(logoName).tag()
        except KeyError:
            self.logo_tag = ''

        self.portal_title = self.portal_state.portal_title()


class GlobalSectionsTile(Tile):
    """A global sections tile."""

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        context = aq_inner(self.context)
        portal_tabs_view = getMultiAdapter((context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs()

        self.selected_tabs = self.selectedTabs(portal_tabs=self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']

    def selectedTabs(self, default_tab='index_html', portal_tabs=()):
        plone_url = getToolByName(self.context, 'portal_url')()
        plone_url_len = len(plone_url)
        request = self.request
        valid_actions = []

        url = request['URL']
        path = url[plone_url_len:]

        for action in portal_tabs:
            if not action['url'].startswith(plone_url):
                # In this case the action url is an external link. Then, we
                # avoid issues (bad portal_tab selection) continuing with next
                # action.
                continue
            action_path = action['url'][plone_url_len:]
            if not action_path.startswith('/'):
                action_path = '/' + action_path
            if path.startswith(action_path):
                # Make a list of the action ids, along with the path length
                # for choosing the longest (most relevant) path.
                valid_actions.append((len(action_path), action['id']))

        # Sort by path length, the longest matching path wins
        valid_actions.sort()
        if valid_actions:
            return {'portal': valid_actions[-1][1]}

        return {'portal': default_tab}


class PathBarTile(Tile):
    """A path bar tile."""

    def __call__(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.navigation_root_url = self.portal_state.navigation_root_url()

        self.update()
        return self.index()

    def update(self):
        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()


class MenuLinkTile(Tile):
    """An menu link tile."""

    def getLink(self):
        return self.context.absolute_url()+"/@@cmsui-menu"

    def showCMSUI(self):
        if not _checkPermission('Plone: View CMS UI',
                                self.context):
            return False
        else:
            return True

class EditBarTile(Tile):
    """A edit bar tile."""

    @memoize
    def prepareObjectTabs(self, default_tab='view',
                          sort_first=['folderContents']):
        """Prepare the object tabs by determining their order and working
        out which tab is selected. Used in global_contentviews.pt
        """
        context = aq_inner(self.context)
        context_url = context.absolute_url()
        context_fti = context.getTypeInfo()

        context_state = getMultiAdapter(
            (context, self.request), name=u'plone_context_state')
        actions = context_state.actions

        action_list = []
        if context_state.is_structural_folder():
            action_list = actions('folder')
        action_list.extend(actions('object'))

        tabs = []
        found_selected = False
        fallback_action = None

        # we use the context-acquired request object here, which is
        # different from the request fetching the tile HTML
        request_url = self.context.REQUEST['ACTUAL_URL']
        request_url_path = request_url[len(context_url):]

        if request_url_path.startswith('/'):
            request_url_path = request_url_path[1:]

        for action in action_list:
            item = {'title': action['title'],
                    'id': action['id'],
                    'url': '',
                    'selected': False}

            action_url = action['url'].strip()
            starts = action_url.startswith
            if starts('http') or starts('javascript'):
                item['url'] = action_url
            else:
                item['url'] = '%s/%s' % (context_url, action_url)

            action_method = item['url'].split('/')[-1]

            # Action method may be a method alias:
            # Attempt to resolve to a template.
            action_method = context_fti.queryMethodID(
                action_method, default=action_method)
            if action_method:
                request_action = unquote(request_url_path)
                request_action = context_fti.queryMethodID(
                    request_action, default=request_action)
                if action_method == request_action:
                    item['selected'] = True
                    found_selected = True

            current_id = item['id']
            if current_id == default_tab:
                fallback_action = item

            tabs.append(item)

        if not found_selected and fallback_action is not None:
            fallback_action['selected'] = True

        def sortOrder(tab):
            try:
                return sort_first.index(tab['id'])
            except ValueError:
                return 255

        tabs.sort(key=sortOrder)
        return tabs

    def object_actions(self):
        context = aq_inner(self.context)
        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')

        return context_state.actions('object_actions')

    def icon(self, action):
        return action.get('icon', None)


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
            self.messages = []


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
        if not _checkPermission('CMFEditions: Access previous versions',
                                self.context):
            return False
        else:
            return True

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
            lockable = getattr(context.aq_explicit,
                               'wl_isLocked', None) is not None
            locked = lockable and context.wl_isLocked()

        if not locked:
            return ""

        portal = self.portal_state.portal()
        icon = portal.restrictedTraverse('lock_icon.gif')
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


class LockInfoTile(Tile):
    """A lockinfo tile."""

    def __call__(self):
        if not self.available() or not ITTWLockable.providedBy(self.context):
            return '<html></html>'
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.update()
        return self.index()

    def available(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission('Modify portal content',
                                          self.context)

    def update(self):
        self.info = getMultiAdapter((self.context, self.request),
                                    name='plone_lock_info')
        self.lock_is_stealable = self.info.lock_is_stealable()
        self.lock_info = self.info.lock_info


class NextPreviousTile(Tile):
    """Tile for showing the next / previous links, based on nextprevious
    viewlets in p.a.layout.
    """

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.npview = self.context.restrictedTraverse(
            '@@plone_nextprevious_view')


class DocumentActionsTile(Tile):
    """Shows the document actions."""

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.actions = self.context_state.actions('document_actions')


class RelatedItemsTile(Tile):
    """A related items tile."""

    def related_items(self):
        context = aq_inner(self.context)
        related = ()

        if base_hasattr(context, 'relatedItems'):
            related = context.relatedItems

        return related


class HistoryTile(Tile):
    """Provides the history as tile. Basically just renders
    the @@contenthistorypopup view, which includes version / content
    history and workflow history.
    """

    def __call__(self):
        view = self.context.restrictedTraverse('@@contenthistorypopup')
        return view()


class LanguageSelectorTile(Tile):
    """Shows the language selector."""

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.tool = getToolByName(self.context, 'portal_languages', None)

    def available(self):
        if self.tool is not None:
            return self.tool.showSelector()
        return False

    def portal_url(self):
        portal_tool = getToolByName(self.context, 'portal_url', None)
        if portal_tool is not None:
            return portal_tool.getPortalObject().absolute_url()
        return None

    def languages(self):
        """Returns list of languages."""
        if self.tool is None:
            return []

        bound = self.tool.getLanguageBindings()
        current = bound[0]

        def merge(lang, info):
            info["code"] = lang
            if lang == current:
                info['selected'] = True
            else:
                info['selected'] = False
            return info

        languages = [merge(lang, info) for (lang, info) in
                        self.tool.getAvailableLanguageInformation().items()
                        if info["selected"]]

        # sort supported languages by index in portal_languages tool
        supported_langs = self.tool.getSupportedLanguages()

        def index(info):
            try:
                return supported_langs.index(info["code"])
            except ValueError:
                return len(supported_langs)

        return sorted(languages, key=index)

    def showFlags(self):
        """XXX: Do we use flags?."""
        if self.tool is not None:
            return self.tool.showFlags()
        return False
