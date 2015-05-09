# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.browser.comments import CommentsViewlet
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from plone.tiles import Tile
from plone.z3cform import z2
from z3c.form.interfaces import IFormLayer
from zope.component import queryUtility
from zope.interface import alsoProvides


# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

from plone.z3cform import layout

#CommentFormView = layout.wrap_form(CommentForm)


class ConversationView(object):
    """Discussion is allowed if it is globally enabled."""

    def enabled(self):
        # Fetch discussion registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        # Check if discussion is allowed globally
        if not settings.globally_enabled:
            return False

        return True


class DiscussionForm(CommentForm):

    @property
    def action(self):
        """ Return the tile url for posting form data, use page url when redirecting
        after a post.
        """
        if 'form.buttons.comment' in self.request.keys():
            return self.context.absolute_url()
        else:
            return self.request.ACTUAL_URL


class DiscussionTile(Tile, CommentsViewlet, layout.FormWrapper):
    """Discussion tile."""

    form = CommentForm
    # index = ViewPageTemplateFile('templates/discussion.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _wrap_viewlet(self, render):
        return u"<html><body>%s</body></html>" % render

    def __call__(self):
        form_data = self.request.form
        self.request = self.context.REQUEST
        self.request.URL = self.context.absolute_url()
        self.form = DiscussionForm(aq_inner(self.context), self.request)
        alsoProvides(self.form, IWrappedForm)
        # wrap the form inside the page
        z2.switch_on(self.form, request_layer=IFormLayer)
        self.form.update()

        if form_data:
            self.form.extractData()

        return self._wrap_viewlet(self.index())
