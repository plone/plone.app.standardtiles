#-*- coding: utf-8 -*-
from plone.portlets.interfaces import IPortletManager
from plone.app.standardtiles import PloneMessageFactory as _
from zope.interface import implements
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory


PORTLET_MANAGER = 'plone.app.standardtiles.portletManager'


class BaseVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = self.get_terms(context)
        return SimpleVocabulary(list(terms))

    def get_dict(self):
        return dict(self.terms)

    def get_terms(self, context):
        raise NotImplementedError()


class PortletsVocab(BaseVocabulary):

    def get_terms(self, context):
        if hasattr(context, 'REQUEST'):
            request = context.REQUEST
        else:
            request = getRequest()

        manager = getUtility(IPortletManager,
                             name=PORTLET_MANAGER)

        # view = context.restrictedTraverse('@@plone')

        # XXX: not working
        # manager_renderer = getMultiAdapter(
        #     (context,
        #      request,
        #      view,
        #      manager),
        #     IPortletManagerRenderer
        # )
        # portlets = manager_renderer.addable_portlets()
        portlets = manager.getAddablePortletTypes()
        yield SimpleTerm(value=None, token='',
                         title=_(u'-- select type --'))
        for item in portlets:
            title = item.title
            token = value = item.addview
            yield SimpleTerm(value=value,
                             token=token,
                             title=title)
