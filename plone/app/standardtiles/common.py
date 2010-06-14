from plone.tiles.tile import Tile
from datetime import date
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Acquisition import aq_inner
from AccessControl import getSecurityManager


class FooterTile(Tile):
    """A footer tile
    """

    @property
    def year(self):
        return date.today().year


class SiteActionsTile(Tile):
    """A site actions tile
    """

    def site_actions(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.actions('site_actions')


class AnalyticsTile(Tile):
    """A analytics tile
    """

    def __call__(self):
        ptool = getToolByName(self.context, "portal_properties")
        snippet = safe_unicode(ptool.site_properties.webstats_js)
        return "<html><body>%s</body></html>" % snippet


class SkipLinksTile(Tile):
    """A skip links tile
    """

    @property
    def current_page_url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.current_page_url


class PersonalBarTile(Tile):
    """A personal bar tile
    """

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
