from AccessControl.ZopeGuards import guarded_hasattr
from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.layout.globals.interfaces import IViewView
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.memoize.view import memoize
from plone.tiles.tile import Tile
from Products.CMFCore.utils import getToolByName
from zope.browser.interfaces import IBrowserView
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.security import checkPermission
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager

import Acquisition
import logging


logger = logging.getLogger(__name__)


class BaseViewletTile(Tile):
    def __init__(self, context, *args, **kwargs):
        # Fix issue where context is a template based view class
        while IBrowserView.providedBy(context) and context is not None:
            context = Acquisition.aq_parent(Acquisition.aq_inner(context))
        super().__init__(context, *args, **kwargs)

    def get_viewlet(self, manager_name, viewlet_name):
        # check visibility
        storage = queryUtility(IViewletSettingsStorage)
        if storage is None:
            return

        skinname = self.context.getCurrentSkinName()

        hidden = frozenset(storage.getHidden(manager_name, skinname))
        if viewlet_name in hidden:
            return

        # get viewlet instance
        manager = queryMultiAdapter(
            (self.context, self.request, self), IViewletManager, name=manager_name
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager), IViewlet, name=viewlet_name
        )
        if viewlet is None:
            logger.debug(
                "Viewlet tile {} in manager {}. "
                "Was not found.".format(viewlet_name, manager_name)
            )
            return

        # check permissions - same as in plone.app.viewletmanager
        if IAcquirer.providedBy(viewlet):
            viewlet = viewlet.__of__(viewlet.context)
        if not guarded_hasattr(viewlet, "render"):
            logger.warn(
                "Blocked attempt to render tile {} in manager {}. "
                "Permission denied.".format(viewlet_name, manager_name)
            )
            return

        return viewlet


class ProxyViewletTile(BaseViewletTile):
    section = "body"
    manager = None
    viewlet = None

    def __call__(self):
        alsoProvides(self, IViewView)
        viewlet = self.get_viewlet(self.manager, self.viewlet)
        if viewlet is None:
            return "<html></html>"

        viewlet.update()
        return "<html><{section}>{rendered}</{section}></html>".format(
            rendered=viewlet.render(), section=self.section
        )


class FooterTile(ProxyViewletTile):
    """A footer tile."""

    manager = "plone.portalfooter"
    viewlet = "plone.footer"


class ColophonTile(ProxyViewletTile):
    """A colophon tile."""

    manager = "plone.portalfooter"
    viewlet = "plone.colophon"


class SiteActionsTile(ProxyViewletTile):
    """A site actions tile."""

    manager = "plone.portalfooter"
    viewlet = "plone.site_actions"


class AnalyticsTile(ProxyViewletTile):
    """A analytics tile."""

    manager = "plone.portalfooter"
    viewlet = "plone.analytics"


class LoginTile(Tile):
    """Login tile."""

    def __init__(self, context, request):
        # Fix issue where context is a template based view class
        while IBrowserView.providedBy(context) and context is not None:
            context = Acquisition.aq_parent(Acquisition.aq_inner(context))
        super().__init__(context, request)

    def __call__(self):
        request = self.request
        self.membership = getToolByName(self.context, "portal_membership")
        self.context_state = getMultiAdapter(
            (self.context, request), name="plone_context_state"
        )
        self.portal_state = getMultiAdapter(
            (self.context, request), name="plone_portal_state"
        )
        self.pas_info = getMultiAdapter((self.context, request), name="pas_info")
        self.navigation_root_url = self.portal_state.navigation_root_url()

        self.update()
        return self.index()

    def show(self):
        if not self.portal_state.anonymous():
            return False
        if not self.pas_info.hasLoginPasswordExtractor():
            return False
        page = self.request.get("URL", "").split("/")[-1]
        return page not in ("login_form", "@@register")

    @property
    def available(self):
        return self.auth() is not None and self.show()

    def login_form(self):
        return "%s/login_form" % self.portal_state.portal_url()

    def mail_password_form(self):
        return "%s/mail_password_form" % self.portal_state.portal_url()

    def login_name(self):
        auth = self.auth()
        name = None
        if auth is not None:
            name = getattr(auth, "name_cookie", None)
        if not name:
            name = "__ac_name"
        return name

    def login_password(self):
        auth = self.auth()
        passwd = None
        if auth is not None:
            passwd = getattr(auth, "pw_cookie", None)
        if not passwd:
            passwd = "__ac_password"
        return passwd

    def join_action(self):
        context = self.context
        tool = getToolByName(context, "portal_actions")
        join = tool.listActionInfos(action_chain="user/join", object=context)
        if len(join) > 0:
            return join[0]["url"]
        return

    def can_register(self):
        if getToolByName(self.context, "portal_registration", None) is None:
            return False
        return self.membership.checkPermission("Add portal member", self.context)

    def can_request_password(self):
        return self.membership.checkPermission("Mail forgotten password", self.context)

    @memoize
    def auth(self, _marker=[]):
        acl_users = getToolByName(self.context, "acl_users")
        return getattr(acl_users, "credentials_cookie_auth", None)

    def update(self):
        pass


class PersonalBarTile(ProxyViewletTile):
    """A personal bar tile."""

    manager = "plone.portalheader"
    viewlet = "plone.membertools"


class SearchBoxTile(ProxyViewletTile):
    """A search box tile."""

    manager = "plone.portalheader"
    viewlet = "plone.searchbox"


class AnonToolsTile(ProxyViewletTile):
    """An anon tools tile."""

    manager = "plone.portalheader"
    viewlet = "plone.anontools"


class LogoTile(ProxyViewletTile):
    """A logo tile."""

    manager = "plone.portalheader"
    viewlet = "plone.logo"


class GlobalSectionsTile(ProxyViewletTile):
    """A global sections tile."""

    manager = "plone.mainnavigation"
    viewlet = "plone.global_sections"


class PathBarTile(ProxyViewletTile):
    """A path bar tile."""

    manager = "plone.abovecontent"
    viewlet = "plone.path_bar"


class ToolbarTile(Tile):
    """A Plone 5 toolbar tile."""

    def __init__(self, context, request):
        # Fix issue where context is a template based view class
        while IBrowserView.providedBy(context) and context is not None:
            context = Acquisition.aq_parent(Acquisition.aq_inner(context))
        super().__init__(context, request)

    def __call__(self):
        mtool = getToolByName(self.context, "portal_membership")
        if mtool.isAnonymousUser():
            return "<html></html>"

        toolbar = getMultiAdapter((self.context, self.request), name="render-toolbar")
        alsoProvides(toolbar, IViewView)
        return "<html><body>%s</body></html>" % toolbar()


class GlobalStatusMessageTile(ProxyViewletTile):
    """Display messages to the current user"""

    manager = "plone.globalstatusmessage"
    viewlet = "plone.globalstatusmessage"


class DocumentBylineTile(ProxyViewletTile):
    """A document byline tile."""

    manager = "plone.belowcontenttitle"
    viewlet = "plone.documentbyline"


class LockInfoTile(ProxyViewletTile):
    """A lockinfo tile."""

    manager = "plone.abovecontent"
    viewlet = "plone.lockinfo"

    def __call__(self):
        if checkPermission("cmf.ModifyPortalContent", self.context):
            return super().__call__()
        else:
            return "<html></html>"


class NextPreviousTile(BaseViewletTile):
    """Tile for showing the next / previous links, based on nextprevious
    viewlets in p.a.layout.
    """

    def __call__(self):
        alsoProvides(self, IViewView)
        links_viewlet = self.get_viewlet(
            "plone.htmlhead.links", "plone.nextprevious.links"
        )
        viewlet = self.get_viewlet("plone.belowcontent", "plone.nextprevious")
        if links_viewlet and viewlet:
            links_viewlet.update()
            viewlet.update()
            try:
                # XXX: We need to cheat viewlet.isViewTemplate:
                url = self.request.get("ACTUAL_URL")
                self.request.set("ACTUAL_URL", self.context.absolute_url())
                return "<html><head>{}</head><body>{}</body></html>".format(
                    links_viewlet.render(),
                    viewlet.render(),
                )
            finally:
                self.request.set("ACTUAL_URL", url)
        return "<html></html>"


class KeywordsTile(ProxyViewletTile):
    """A tile that displays the context's keywords, if any."""

    manager = "plone.belowcontentbody"
    viewlet = "plone.keywords"


class TableOfContentsTile(ProxyViewletTile):
    """A Table of contents tile."""

    manager = "plone.abovecontentbody"
    viewlet = "plone.tableofcontents"


class LeadImageTile(Tile):
    """A tile that displays lead image, when available"""

    available = False

    def __call__(self):
        adapted = ILeadImage(self.context, None)
        try:
            if adapted is not None and aq_base(adapted).image is not None:
                self.context = adapted
                self.available = True
        except AttributeError:
            pass
        if self.available:
            tile = self.index()
        else:
            tile = ""
        return f"<html><body>{tile:s}</body></html>"


class DocumentActionsTile(ProxyViewletTile):
    """Shows the document actions."""

    manager = "plone.belowcontent"
    viewlet = "plone.documentactions"


class RelatedItemsTile(ProxyViewletTile):
    """A related items tile."""

    manager = "plone.belowcontentbody"
    viewlet = "plone.relateditems"


class HistoryTile(Tile):
    """Provides the history as tile. Basically just renders
    the @@contenthistorypopup view, which includes version / content
    history and workflow history.
    """

    def __call__(self):
        return self.context.restrictedTraverse("@@contenthistorypopup")()


class LanguageSelectorTile(ProxyViewletTile):
    """Shows the language selector."""

    manager = "plone.portalheader"
    viewlet = "plone.app.multilingual.languageselector"
