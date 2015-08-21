# -*- coding: utf-8 -*-

# this tile will not be registered in the registry
# because it is assumed this will only be used in layouts
# and not added to custom layouts since custom layouts will
# use normal text input

from plone.app.standardtiles import _PMF as _
from plone.supermodel.model import Schema
from plone.tiles import PersistentTile
from zope import schema


class IRawHTMLTile(Schema):

    content = schema.Text(
        title=_(u"HTML"),
        required=True
    )


class RawHTMLTile(PersistentTile):
    def __call__(self):
        return u"<html><body>%s</body></html>" % (self.data.get('content') or '<p></p>')
