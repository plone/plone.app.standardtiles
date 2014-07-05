# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import url_quote
from cgi import escape
from plone.tiles.tile import Tile
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope import schema
from zope.interface import Interface
from zope.interface import implements
from plone.app.standardtiles import PloneMessageFactory as _


class TitleTile(Tile):
    """A tile rendering the title tag to be inserted in the HTML headers."""

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


class IStylesheetsTile(Interface):

    theme = schema.TextLine(
        title=_(u"Name of the theme"),
        required=False
    )


class StylesheetsTile(Tile):
    """A stylesheets rendering tile."""

    implements(IStylesheetsTile)

    def registry(self):
        return getToolByName(aq_inner(self.context), 'portal_css')

    def skinname(self):
        # Return the explicitly given skinname
        skinname = self.data.get('theme')
        if skinname:
            return skinname

        # Or look up the skinname of the context or first parent with one
        context = self.context
        while context is not None:
            try:
                return aq_inner(context).getCurrentSkinName()
            except AttributeError:
                context = aq_parent(aq_inner(context))
        return getSite().getCurrentSkinName()

    def styles(self):
        registry = self.registry()
        registry_url = registry.absolute_url()
        context = aq_inner(self.context)

        skinname = self.skinname()
        styles = registry.getEvaluatedResources(context, theme=skinname)

        skinpath = url_quote(skinname)
        result = []
        for style in styles:
            rendering = style.getRendering()
            if style.isExternalResource():
                src = "%s" % style.getId()
            else:
                src = "%s/%s/%s" % (registry_url, skinpath, style.getId())
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
                    "Unkown rendering method '%s' for style '%s'" %
                    (rendering, style.getId())
                )
            result.append(data)
        return result


class IJavascriptsTile(Interface):

    theme = schema.TextLine(
        title=_(u"Name of the theme"),
        required=False
    )


class JavascriptsTile(Tile):
    """A javascripts rendering tile."""

    implements(IJavascriptsTile)

    def registry(self):
        return getToolByName(aq_inner(self.context), 'portal_javascripts')

    def skinname(self):
        # Return the explicitly given skinnam
        skinname = self.data.get('theme')
        if skinname:
            return skinname

        # Or look up the skinname of the context or first parent with one
        context = self.context
        while context is not None:
            try:
                return aq_inner(context).getCurrentSkinName()
            except AttributeError:
                context = aq_parent(aq_inner(context))
        return getSite().getCurrentSkinName()

    def scripts(self):
        registry = self.registry()
        registry_url = registry.absolute_url()
        context = aq_inner(self.context)

        skinname = self.skinname()
        scripts = registry.getEvaluatedResources(context, theme=skinname)

        skinpath = url_quote(skinname)
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
                    src = "%s/%s/%s" % (registry_url, skinpath, script.getId())
                data = {'inline': inline,
                        'conditionalcomment': script.getConditionalcomment(),
                        'src': src}
            result.append(data)
        return result


class FaviconLinkTile(Tile):
    """Favicon link tile implementation."""

    @property
    def site_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.portal_url()


class AuthorLinkTile(Tile):
    """Author link tile implementation."""

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
    """Navigation link tile implementation."""

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.navigation_root_url()


class SearchLinkTile(Tile):
    """Search link tile implementation."""

    @property
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.navigation_root_url()


class RSSLinkTile(Tile):
    """RSS link tile implementation."""

    def allowed(self):
        syntool = getToolByName(self.context, 'portal_syndication')
        try:
            return syntool.isSyndicationAllowed(self.context)
        except TypeError:  # Could not adapt
            return False

    @property
    def url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return '%s/RSS' % context_state.object_url()
