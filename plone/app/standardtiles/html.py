# -*- coding: utf-8 -*-
from plone.app.standardtiles import _PMF as _
from plone.supermodel.model import Schema
from plone.tiles import PersistentTile
from Products.CMFCore.utils import getToolByName
from zope import schema


class IHTMLTile(Schema):

    content = schema.Text(
        title=_(u"HTML"),
        required=True
    )


class HTMLTile(PersistentTile):
    def __call__(self):
        content = self.data.get('content')
        if content:
            # only transform is not rendering for layout editor
            if not self.request.get('_layouteditor'):
                transforms = getToolByName(self.context, 'portal_transforms')
                data = transforms.convertTo('text/x-html-safe', content, mimetype='text/html',
                                            context=self.context)
                content = data.getData()
        else:
            content = u'<p></p>'
        return u"<html><body>%s</body></html>" % content
