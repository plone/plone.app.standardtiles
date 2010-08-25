# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from zope import schema
from zope.interface import implements
from zope.interface import alsoProvides
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IPublishTraverse

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.directives import form as directivesform

from plone.tiles import Tile

from plone.namedfile.utils import set_headers, stream_data
from plone.namedfile.field import NamedFile

from plone.z3cform.interfaces import IWrappedForm
 
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.browser.comments import CommentForm

class DiscussionTile(Tile):
    """Discussion tile.
    """

    form = CommentForm
    index = ViewPageTemplateFile('templates/discussion.pt')
    
    def __call__(self):
        self.form = self.form(aq_inner(self.context), self.request)
        alsoProvides(self.form, IWrappedForm)
        self.form.update()
        return self.form.render()
        
    def update(self):
        pass
