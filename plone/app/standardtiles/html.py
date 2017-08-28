# -*- coding: utf-8 -*-
from plone.app.blocks.layoutbehavior import ILayoutAware
from plone.app.blocks.utils import bodyTileXPath
from plone.app.blocks.utils import replace_with_children
from plone.app.blocks.utils import tileAttrib
from plone.app.standardtiles import _PMF as _
from plone.subrequest import ISubRequest
from plone.supermodel.directives import primary
from plone.supermodel.model import Schema
from plone.tiles.directives import ignore_querystring
from plone.tiles import Tile
from plone.transformchain.interfaces import ITransform
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from repoze.xmliter.serializer import XMLSerializer
from repoze.xmliter.utils import getHTMLSerializer
from zope import schema
from zope.interface import implementer


class IHTMLTile(Schema):

    ignore_querystring('content')
    primary('content')
    content = schema.Text(
        title=_(u"HTML"),
        required=True
    )


class HTMLTile(Tile):
    """
    A persistent HTML content tile that can be used for
    re-usable layouts in the mosaic editor
    """


    def __call__(self):
        content = self.data.get('content')
        if content:
            # only transform if not rendering for layout editor
            if (not self.request.get('_layouteditor') or
                    ISubRequest.providedBy(self.request)):
                transforms = getToolByName(self.context, 'portal_transforms')
                data = transforms.convertTo(
                    'text/x-html-safe',
                    content, mimetype='text/html',
                    context=self.context
                )
                content = data.getData()
        else:
            content = u'<p></p>'
        return u"<html><body>%s</body></html>" % safe_unicode(content)


@implementer(ITransform)
class InlineHTMLTiles(object):
    order = 8200  # must be between panel merge and tile merge

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transform(self, result, encoding):
        # Sanity check that published context is layout aware and has content
        try:
            context = self.published.context
        except AttributeError:
            return None

        adapter = ILayoutAware(context, None)
        if adapter is None:
            return None

        content = adapter.content
        if not content:
            return None

        # Ensure safe html, UUID and image captions transformations
        transforms = getToolByName(context, 'portal_transforms')
        data = transforms.convertTo('text/x-html-safe', content,
                                    mimetype='text/html', context=context)
        content = safe_unicode(data.getData())

        # Parse the result into searchable tile data storage tree
        storage = getHTMLSerializer([content.encode('utf-8')],
                                    pretty_print=True, encoding='utf-8')

        # Iter all HTML tiles and replace them with matching content
        for node in bodyTileXPath(result.tree):
            href = node.attrib[tileAttrib].lstrip('./')
            if not href.startswith('@@plone.app.standardtiles.html'):
                continue
            for html in storage.tree.xpath(
                    '//*[@data-tile="{0:s}"]'.format(href)):
                for child in html.getchildren():
                    replace_with_children(node, child)
                    break
                break

        return result

    def transformBytes(self, result, encoding):
        return None

    def transformUnicode(self, result, encoding):
        return None

    def transformIterable(self, result, encoding):
        if not self.request.get('plone.app.blocks.enabled', False):
            return None

        if not isinstance(result, XMLSerializer):
            return None

        return self.transform(result, encoding)
