# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_quote
from plone.app.standardtiles import PloneMessageFactory as _
from plone.tiles import Tile
from zope import schema
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface import implementer


class IStylesheetsTile(Interface):
    theme = schema.TextLine(
        title=_(u"Name of the theme"),
        required=False
    )


@implementer(IStylesheetsTile)
class StylesheetsTile(Tile):
    """A stylesheets rendering tile."""

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


@implementer(IJavascriptsTile)
class JavascriptsTile(Tile):
    """A javascripts rendering tile."""

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
