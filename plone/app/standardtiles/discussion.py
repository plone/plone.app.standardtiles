# -*- coding: utf-8 -*-
from urllib import quote as url_quote

from Acquisition import aq_inner
from AccessControl import getSecurityManager
from DateTime import DateTime

from zope.component import createObject, queryUtility
from zope.interface import alsoProvides
from z3c.form.interfaces import IFormLayer
from z3c.form import button

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion import PloneAppDiscussionMessageFactory as _
from plone.tiles import Tile
from plone.z3cform import z2

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

from plone.z3cform import layout

#CommentFormView = layout.wrap_form(CommentForm)


class ConversationView(object):
    """ Discussion is allowed if it is globally enabled """

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

class DiscussionTile(Tile, layout.FormWrapper):
    """ Discussion tile. """

    form = CommentForm
    index = ViewPageTemplateFile('templates/discussion.pt')

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

        return self.index()

    def can_reply(self):
        return getSecurityManager().checkPermission('Reply to item',
                                                    aq_inner(self.context))

    def can_manage(self):
        return getSecurityManager().checkPermission('Manage portal',
                                                    aq_inner(self.context))

    def is_discussion_allowed(self):
        return True

    def has_replies(self, workflow_actions=False):
        """Returns true if there are replies.
        """
        if self.get_replies(workflow_actions) is not None:
            try:
                self.get_replies(workflow_actions).next()
                return True
            except StopIteration:
                pass
        return False

    def get_replies(self, workflow_actions=False):
        """Returns all replies to a content object.

        If workflow_actions is false, only published
        comments are returned.

        If workflow actions is true, comments are
        returned with workflow actions.
        """
        context = aq_inner(self.context)
        conversation = IConversation(context)

        wf = getToolByName(context, 'portal_workflow')

        # workflow_actions is only true when user
        # has 'Manage portal' permission

        def replies_with_workflow_actions():
            # Generator that returns replies dict with workflow actions
            for r in conversation.getThreads():
                comment_obj = r['comment']
                # list all possible workflow actions
                actions = [a for a in wf.listActionInfos(object=comment_obj)
                               if a['category'] == 'workflow' and a['allowed']]
                r = r.copy()
                r['actions'] = actions
                yield r

        def published_replies():
            # Generator that returns replies dict with workflow status.
            for r in conversation.getThreads():
                comment_obj = r['comment']
                workflow_status = wf.getInfoFor(comment_obj, 'review_state')
                if workflow_status == 'published':
                    r = r.copy()
                    r['workflow_status'] = workflow_status
                    yield r

        # Return all direct replies
        if conversation.total_comments > 0:
            if workflow_actions:
                return replies_with_workflow_actions()
            else:
                return published_replies()

    def get_commenter_home_url(self, username=None):
        if username is None:
            return None
        else:
            return "%s/author/%s" % (self.context.portal_url(), username)

    def get_commenter_portrait(self, username=None):

        if username is None:
            # return the default user image if no username is given
            return 'defaultUser.gif'
        else:
            portal_membership = getToolByName(self.context,
                                              'portal_membership',
                                              None)
            return portal_membership.getPersonalPortrait(username) \
                .absolute_url()

    def anonymous_discussion_allowed(self):
        # Check if anonymous comments are allowed in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        return settings.anonymous_comments

    def show_commenter_image(self):
        # Check if showing commenter image is enabled in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        return settings.show_commenter_image

    def is_anonymous(self):
        portal_membership = getToolByName(self.context,
                                          'portal_membership',
                                          None)
        return portal_membership.isAnonymousUser()

    def login_action(self):
        return '%s/login_form?came_from=%s' % (self.context,
                                               url_quote(
                                                   self.request.get('URL',
                                                                    '')),)

    def format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        util = getToolByName(self.context, 'translation_service')
        zope_time = DateTime(time.year,
                             time.month,
                             time.day,
                             time.hour,
                             time.minute,
                             time.second)
        return util.toLocalizedTime(zope_time, long_format=True)
