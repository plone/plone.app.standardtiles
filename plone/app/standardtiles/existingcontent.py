# -*- coding: utf-8 -*-
from lxml import etree
from lxml import cssselect

from plone.app.standardtiles import PloneMessageFactory as _ # noqa
from plone.directives import form as directivesform
from plone.tiles import Tile
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import RelatedItemsFieldWidget

from zope import schema


class IExistingContentTile(directivesform.Schema):

    directivesform.widget(content_uid=RelatedItemsFieldWidget)
    content_uid = schema.Choice(
        title=_(u"Select an existing content"),
        required=True,
        source=CatalogSource(),
    )
    css_selector = schema.TextLine(
        title=_(u'CSS selector'),
        description=_(u"Specify a CSS selector "
                      u"to be used for getting "
                      u"the HTML portion to inject."),
        required=True,
        default=u'#content'
    )
    view_name = schema.TextLine(
        title=_(u"View name"),
        required=False,
        default=u'document_view',
        # vocabulary='### what goes here??? should be dynamic'
    )


class ExistingContentTile(Tile):
    """ Existing content tile.
    """

    def get_content(self):
        tools = self.context.restrictedTraverse('@@plone_tools')
        catalog = tools.catalog()
        content_uid = self.data.get('content_uid')
        brain = catalog(UID=content_uid)
        return brain and brain[0] or None

    def content_html(self):
        brain = self.get_content()
        if not brain:
            return ''

        ps = self.context.restrictedTraverse('@@plone_portal_state')
        portal = ps.portal()

        view_name = self.data.get('view_name')
        path = '{path}/{view}'.format(path=brain.getPath(),
                                      view=view_name)

        view = portal.restrictedTraverse(path)
        css_selector = self.data.get('css_selector')

        htmlparser = etree.HTMLParser()
        tree = etree.fromstring(view(), htmlparser)
        sel = cssselect.CSSSelector(css_selector)
        content = sel(tree)
        content_html = ''
        if content:
            content_html = etree.tostring(content[0])
        return content_html
