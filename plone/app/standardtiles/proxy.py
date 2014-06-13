# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from lxml import etree, cssselect
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.standardtiles.source import IntIdSourceBinder
from plone.directives import form as directivesform
from plone.tiles import PersistentTile
from z3c.relationfield.schema import RelationChoice
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class IProxyTile(directivesform.Schema):
    contentId = RelationChoice(title=_(u"Id of the proxied content."),
                               source=IntIdSourceBinder(),
                               required=True)
    contentId._type = int


class ProxyTile(PersistentTile):
    """Proxy tile.

    It renders the @@proxy-view browser view on the specified content
    object.
    """

    def __call__(self):
        contentId = self.data.get('contentId')
        intids = getUtility(IIntIds)
        content = intids.queryObject(int(contentId))
        view = content.restrictedTraverse('@@proxy-view')
        return view()


class ProxyView(BrowserView):

    template = ViewPageTemplateFile('templates/proxy_view.pt')

    def __call__(self):
        out = self.context.restrictedTraverse('view')()
        htmlparser = etree.HTMLParser()
        tree = etree.fromstring(out, htmlparser)
        sel = cssselect.CSSSelector('#content')
        content = sel(tree)[0]
        self.content_html = etree.tostring(content)
        return self.template()
