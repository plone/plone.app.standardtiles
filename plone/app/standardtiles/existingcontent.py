# -*- coding: utf-8 -*-
from plone.app.uuid.utils import uuidToObject
from plone.memoize.view import memoize
from zope.browser.interfaces import IBrowserView
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel import model
from plone.tiles import Tile
from plone.app.vocabularies.catalog import CatalogSource as CatalogSourceBase
from zope import schema


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
        item = uuidToObject(self.data.get('content_uid'))
        return item

    @property
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
            return default_view.index.macros
        elif default_view:
            # FSPageTemplate
            return default_view.macros
        else:
            return None
