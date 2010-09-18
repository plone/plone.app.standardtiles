from cgi import escape
from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.tiles.tile import Tile
from zope.component import getMultiAdapter


class TitleTile(Tile):
    """A tile rendering the title tag to be inserted in the HTML headers.
    """

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                         name=u'plone_context_state')
        page_title = escape(safe_unicode(context_state.object_title()))
        portal_title = escape(safe_unicode(portal_state.portal_title()))
        if page_title == portal_title:
            self.site_title = portal_title
        else:
            self.site_title = u"%s &mdash; %s" % (page_title, portal_title)


class StylesheetsTile(Tile):
    """A stylesheets rendering tile
    """

    def registry(self):
        return getToolByName(aq_inner(self.context), 'portal_css')

    def skinname(self):
        return aq_inner(self.context).getCurrentSkinName()

    def styles(self):
        registry = self.registry()
        registry_url = registry.absolute_url()
        context = aq_inner(self.context)

        styles = registry.getEvaluatedResources(context)
        skinname = url_quote(self.skinname())
        result = []
        for style in styles:
            rendering = style.getRendering()
            if style.isExternalResource():
                src = "%s" % style.getId()
            else:
                src = "%s/%s/%s" % (registry_url, skinname, style.getId())
            if rendering == 'link':
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'rel': style.getRel(),
                        'title': style.getTitle(),
                        'conditionalcomment': style.getConditionalcomment(),
                        'src': src}
            elif rendering == 'import':
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'conditionalcomment': style.getConditionalcomment(),
                        'src': src}
            elif rendering == 'inline':
                content = registry.getInlineResource(style.getId(), context)
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'conditionalcomment': style.getConditionalcomment(),
                        'content': content}
            else:
                raise ValueError(
                    "Unkown rendering method '%s' for style '%s'" % \
                        (rendering, style.getId()))
            result.append(data)
        return result


class JavascriptsTile(Tile):
    """A javascripts rendering tile
    """

    def registry(self):
        return getToolByName(aq_inner(self.context), 'portal_javascripts')

    def skinname(self):
        return aq_inner(self.context).getCurrentSkinName()

    def scripts(self):
        registry = self.registry()
        registry_url = registry.absolute_url()
        context = aq_inner(self.context)

        scripts = registry.getEvaluatedResources(context)
        skinname = url_quote(self.skinname())
        result = []
        for script in scripts:
            inline = bool(script.getInline())
            if inline:
                content = registry.getInlineResource(script.getId(), context)
                data = {'inline': inline,
                        'conditionalcomment': script.getConditionalcomment(),
                        'content': content}
            else:
                if script.isExternalResource():
                    src = "%s" % (script.getId(),)
                else:
                    src = "%s/%s/%s" % (registry_url, skinname, script.getId())
                data = {'inline': inline,
                        'conditionalcomment': script.getConditionalcomment(),
                        'src': src}
            result.append(data)
        return result


class FaviconLinkTile(Tile):
    """Favicon link tile implementation.
    """

    @property
    def site_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.portal_url()


class AuthorLinkTile(Tile):
    """Author link tile implementation.
    """

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.navigation_root_url()

    def show(self):
        tools = getMultiAdapter((self.context, self.request),
                                 name='plone_tools')
        properties = tools.properties()
        site_properties = getattr(properties, 'site_properties')
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        anonymous = portal_state.anonymous()
        allowAnonymousViewAbout = site_properties.getProperty(
            'allowAnonymousViewAbout', True)
        return not anonymous or allowAnonymousViewAbout


class NavigationLinkTile(Tile):
    """Navigation link tile implementation.
    """

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.navigation_root_url()


class SearchLinkTile(Tile):
    """Search link tile implementation.
    """

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.navigation_root_url()


class RSSLinkTile(Tile):
    """RSS link tile implementation.
    """

    def allowed(self):
        syntool = getToolByName(self.context, 'portal_syndication')
        return syntool.isSyndicationAllowed(self.context)

    @property
    def url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                         name=u'plone_context_state')
        self.url = '%s/RSS' % context_state.object_url()
