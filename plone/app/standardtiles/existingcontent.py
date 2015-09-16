# -*- coding: utf-8 -*-
from plone.app.blocks import utils
from plone.app.blocks.tiles import renderTiles
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource as CatalogSourceBase
from plone.memoize.view import memoize
from plone.supermodel import model
from plone.tiles import Tile
from plone.uuid.interfaces import IUUID
from repoze.xmliter.utils import getHTMLSerializer
from zope import schema
from zope.browser.interfaces import IBrowserView


class CatalogSource(CatalogSourceBase):
    """ExistingContentTile specific catalog source to allow targeted widget
    """


class IExistingContentTile(model.Schema):

    content_uid = schema.Choice(
        title=_(u"Select an existing content"),
        required=True,
        source=CatalogSource(),
    )


class ExistingContentTile(Tile):
    """Existing content tile
    """

    @property
    @memoize
    def content_context(self):
        uuid = self.data.get('content_uid')
        if uuid != IUUID(self.context, None):
            item = uuidToObject(uuid)
            if item is not None:
                return item
            else:
                return None
        else:
            return None

    @property
    @memoize
    def default_view(self):
        context = self.content_context
        if context is not None:
            item_layout = context.getLayout()
            default_view = context.restrictedTraverse(item_layout)
            return default_view
        else:
            return None

    @property
    def item_macros(self):
        default_view = self.default_view
        if default_view and IBrowserView.providedBy(default_view):
            # IBrowserView
            if getattr(default_view, 'index', None):
                return default_view.index.macros
            else:
                return None
        elif default_view:
            # FSPageTemplate
            return default_view.macros
        else:
            return None

    @property
    def item_panels(self):
        default_view = self.default_view
        html = default_view()
        if isinstance(html, unicode):
            html = html.encode('utf-8')
        serializer = getHTMLSerializer([html], pretty_print=False,
                                       encoding='utf-8')
        panels = dict(
            (node.attrib['data-panel'], node)
            for node in utils.panelXPath(serializer.tree)
        )
        if panels:
            request = self.request.clone()
            request.URL = self.content_context.absolute_url() + '/'
            try:
                renderTiles(request, serializer.tree)
            except RuntimeError:  # maximum recursion depth exceeded
                return []
            clear = '<div style="clear: both;"></div>'
            return [''.join([serializer.serializer(child)
                             for child in node.getchildren()])
                    for name, node in panels.items()] + [clear]
        else:
            return []
