# -*- coding: utf-8 -*-

# this tile will not be registered in the registry
# because it is assumed this will only be used in layouts
# and not added to custom layouts since custom layouts will
# use normal text input
from plone.app.standardtiles import _PMF as _
from plone.outputfilters import apply_filters
from plone.outputfilters.interfaces import IFilter
from plone.supermodel.model import Schema
from plone.tiles import PersistentTile
from zope import schema
from zope.component import getAdapters


class IRawHTMLTile(Schema):

    content = schema.Text(
        title=_(u"HTML"),
        required=True
    )


class RawHTMLTile(PersistentTile):
    def __call__(self):
        content = self.data.get('content')
        if content:
            # Here we skip legacy portal_transforms and call
            # plone.outputfilters directly by purpose
            filters = [f for _, f
                       in getAdapters((self.context, self.request), IFilter)]
            content = apply_filters(filters, content)
        else:
            content = u'<p></p>'
        return u"<html><body>%s</body></html>" % content
