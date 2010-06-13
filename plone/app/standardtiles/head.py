from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.tiles.tile import Tile
from zope.component import getMultiAdapter


class ResourceRegistriesTile(Tile):
    """Information for resource registry rendering.
    """

    def css_registry(self):
        return getToolByName(aq_inner(self.context), 'portal_css')

    def javascripts_registry(self):
        return getToolByName(aq_inner(self.context), 'portal_javascripts')

    def skinname(self):
        return aq_inner(self.context).getCurrentSkinName()

    def styles(self):
        registry = self.css_registry()
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
                        'conditionalcomment' : style.getConditionalcomment(),
                        'src': src}
            elif rendering == 'import':
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'conditionalcomment' : style.getConditionalcomment(),
                        'src': src}
            elif rendering == 'inline':
                content = registry.getInlineResource(style.getId(), context)
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'conditionalcomment' : style.getConditionalcomment(),
                        'content': content}
            else:
                raise ValueError("Unkown rendering method '%s' for style '%s'" % (rendering, style.getId()))
            result.append(data)
        return result

    def scripts(self):
        registry = self.javascrips_registry()
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
                        'conditionalcomment' : script.getConditionalcomment(),
                        'content': content}
            else:
                if script.isExternalResource():
                    src = "%s" % (script.getId(),)
                else:
                    src = "%s/%s/%s" % (registry_url, skinname, script.getId())
                data = {'inline': inline,
                        'conditionalcomment' : script.getConditionalcomment(),
                        'src': src}
            result.append(data)
        return result


class FaviconTile(Tile):
    """Favicon tile implementation.
    """

    @property
    def site_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.portal_url()


class AuthorTile(Tile):
    """Author tile implementation.
    """

    @property
    def site_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.portal_url()

    def show(self):
        tools = getMultiAdapter((self.context, self.request),
                                 name='plone_tools')
        properties = tools.properties()
        site_properties = getattr(properties, 'site_properties')
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        anonymous = portal_state.anonymous()
        allowAnonymousViewAbout = site_properties.getProperty('allowAnonymousViewAbout', True)
        return not anonymous or allowAnonymousViewAbout
