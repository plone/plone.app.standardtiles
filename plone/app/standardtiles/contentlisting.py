# -*- coding: utf-8 -*-
import re
import json
from operator import itemgetter
from lxml import etree
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.z3cform.widget import QueryStringFieldWidget
from plone.autoform.directives import widget
from plone.supermodel.directives import primary
from plone.autoform.directives import omitted
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from plone.tiles import Tile
from plone.tiles.interfaces import ITileType
from plone.tiles.directives import ignore_querystring
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.subrequest import ISubRequest
from z3c.form.interfaces import IValue
from z3c.form.util import getSpecification
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
from zope.schema import getFields
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class IContentListingTile(Schema):
    """A tile that displays a listing of content items"""

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False
    )

    ignore_querystring('content')
    primary('content')
    # omitted('content')
    content = schema.Text(
        title=_(u"HTML"),
        required=False,
        default=_(u"""
    <p>
        <span class="mosaic-ILeadImage-image-tile mosaic-tile-inline mceNonEditable" contenteditable="false">
            <span class="mosaic-inline-tile-content">
                <span data-tile="./@@plone.app.standardtiles.field?field=ILeadImage-image">
                </span>
            </span>
        </span> 
        <span class="mosaic-IDublinCore-title-tile mosaic-tile-inline mceNonEditable" contenteditable="false">
            <span class="mosaic-rich-text mosaic-inline-tile-content">
                <span data-tile="./@@plone.app.standardtiles.field?field=IDublinCore-title">
                </span>
            </span>
        </span>
        <span class="mosaic-IDublinCore-description-tile mosaic-tile-inline mceNonEditable" contenteditable="false">
            <span class="mosaic-rich-text mosaic-inline-tile-content">
                <span data-tile="./@@plone.app.standardtiles.field?field=IDublinCore-description">
                </span>
            </span>
        </span>
    ​</p>
    """)
    )


    description = schema.Text(
        title=_(u'label_description', default=u'Summary'),
        description=_(
            u'help_description',
            default=u'Used in item listings and search results.'
        ),
        required=False,
        missing_value=u'',
    )

    widget(query=QueryStringFieldWidget)
    query = schema.List(
        title=_(u"Search terms"),
        value_type=schema.Dict(
            value_type=schema.Field(),
            key_type=schema.TextLine()
        ),
        description=_(u'Define the search terms for the items '
                      u'you want to list by choosing what to match on. The '
                      u'list of results will be dynamically updated'),
        required=False
    )

    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'Sort on'),
        description=_(u'Sort the collection on this index'),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_(u'label_sort_reversed', default=u'Reversed order'),
        description=_(u'Sort the results in reversed order'),
        required=False,
    )

    limit = schema.Int(
        title=_(u'Limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=100,
        min=1,
    )

    view_template = schema.Choice(
        title=_(u'Display mode'),
        source=_(u'Available Listing Views'),
        required=False
    )

class IContentListingTileLayer(Interface):
    """Layer (request marker interface) for content listing tile views"""


@implementer(IValue)
@adapter(
    None,
    None,
    None,
    getSpecification(IContentListingTile['query']),
    None
)
class DefaultQuery(object):
    def __init__(self, context, request, form, field, widget):
        self.context = context

    def get(self):
        if IFolderish.providedBy(self.context):
            value = '::1'
        else:
            value = '..::1'
        return [{
            'i': 'path',
            'o': 'plone.app.querystring.operation.string.relativePath',
            'v': value
        }]


@implementer(IValue)
@adapter(
    None,
    None,
    None,
    getSpecification(IContentListingTile['sort_on']),
    None
)
class DefaultSortOn(object):
    def __init__(self, context, request, form, field, widget):
        pass

    def get(self):
        return 'getObjPositionInParent'


class ContentListingTile(Tile):
    """A tile that displays a listing of content items"""

    template = ViewPageTemplateFile('templates/contentlisting_view.pt')

    itemtemplate = ''

    default_html = """
    <html>
    </html>
    """

    def __call__(self):
        self.update()
        return self.template()

    def update(self):
        self.query = self.data.get('query')
        self.sort_on = self.data.get('sort_on')

        if self.query is None or self.sort_on is None:
            # Get defaults
            tileType = queryUtility(ITileType, name=self.__name__)
            fields = getFields(tileType.schema)
            if self.query is None:
                self.query = getMultiAdapter((
                    self.context,
                    self.request,
                    None,
                    fields['query'],
                    None
                ), name='default').get()
            if self.sort_on is None:
                self.sort_on = getMultiAdapter((
                    self.context,
                    self.request,
                    None,
                    fields['sort_on'],
                    None
                ), name='default').get()

        self.limit = self.data.get('limit')
        if self.data.get('sort_reversed'):
            self.sort_order = 'reverse'
        else:
            self.sort_order = 'ascending'
        self.view_template = self.data.get('view_template')

    @property
    def title(self):
        return self.data.get('title')

    @property
    def html(self):
        if (self.request.get('_layouteditor')):
            return safe_unicode(self.data.get('content'))
        else:
            return safe_unicode(u'<p></p>')


    @property
    def description(self):
        return self.data.get('description')

    def contents(self):
        """Search results"""
        builder = getMultiAdapter(
            (self.context, self.request),
            name='querybuilderresults'
        )
        accessor = builder(
            query=self.query,
            sort_on=self.sort_on or 'getObjPositionInParent',
            sort_order=self.sort_order,
            limit=self.limit
        )
        view = self.view_template or 'listing_view'
        view = view.encode('utf-8')
        alsoProvides(self.request, IContentListingTileLayer)
        contentlisting = getMultiAdapter((accessor, self.request), name=view).context
        options = dict(original_context=self.context,
                       context=contentlisting)
        if(self.data.get('content')) :
            entrycontent = self.data.get('content')
        else:
            entrycontent = self.default_html
            self.data['content'] = self.default_html
        self.itemtemplate = generatetemplate(entrycontent)
        obj = ViewPageTemplateString(self.itemtemplate)
        return obj(self,**options)
        # return getMultiAdapter((accessor, self.request), name=view)(**options)

html_template = """
    <html xmlns="http://www.w3.org/1999/xhtml"
      xml:lang="en"
      lang="en"
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
      i18n:domain="plone">
        <body>
            <tal:defines define="results nocall:options/context">
                <tal:listing condition="results">
                    <dl class="listing">
                    <dt>
                        <tal:entry repeat="item results">
                        </tal:entry>
                    </dt>
                    </dl>
                    </tal:listing>
            </tal:defines>
        </body>
    </html>
    """

table_template = """
    <html xmlns="http://www.w3.org/1999/xhtml"
      xml:lang="en"
      lang="en"
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
      i18n:domain="plone">
        <body>
            <tal:defines define="results nocall:options/context">
                <tal:listing condition="results">
                    <table class="listing">
                    <tbody>
                        <tal:entry repeat="item results">
                        </tal:entry>
                    </tbody>
                    </table>
                    </tal:listing>
            </tal:defines>
        </body>
    </html>
    """

def generatetemplate(entrycontent):
    content = etree.HTML(entrycontent)
    #If there is a table present in content, see if it should be repeated
    table = content.find('.//table/*')
    if(table and isTable(content, False)):
        outer = etree.fromstring(table_template)
        replaceTiles(table)
    else:
        outer = etree.fromstring(html_template)
        replaceTiles(content)
    #etree.HTML() adds html and body tags so we find nodes inside them
    contentBody = content.xpath('.//body/*')
    for child in contentBody:
        outer.find('.//{%s}entry' % '*')\
            .append(child)
    return etree.tostring(outer)

def isTable(element, insideTable):
    """Checks if all the inline tiles in
    element are inside a table"""
    for child in element:
        isTile = child.xpath('./@data-tile')
        # import pdb
        # pdb.set_trace()
        if(isTile and not insideTable):
            return False
        else:
            if (child.tag is 'table'):
                insideTable = True
            return isTable(child, insideTable)
    return True


def replaceTiles(element):
    """Go through elements in item layout html and replace tile references
    with <tal:content>"""
    for child in element:
        classes = child.xpath('./@data-tile')
        tag = child.tag
        if (classes):
            listfield = re.search('listfieldtile', classes[0])
            if(listfield):
                tileClass = re.search('\?field=(.*)', classes[0])
                if (tileClass):
                    field = tileClass.group(1)
                    if(field):
                        htmlstring = '<' + tag + '>' '<' + tag + ' tal:condition="python: callable(item.' + field + ')" ' \
                             'tal:content="python: item.' + field + '()" >' \
                            '</' + tag + '>' \
                            '<' + tag + \
                            ' tal:condition="python:not callable(item.' + field + ')" tal:content="item/' \
                            + field + '">' \
                            '</' + tag + '>' '</' + tag + '>'
                        talNode = etree.HTML(htmlstring)
                        # for tileurl in talNode.xpath('./@data-tileurl'):
                        #     tileurl.getparent().remove(tileurl)
                        # element.replace(
                        #     child, talNode.find('.//body/*'))
                        #This is a tad silly
                        element.getparent().getparent().replace(
                            element.getparent(), talNode.find('.//body/*'))
                        # import pdb
                        # pdb.set_trace()
            else:
                tileClass = re.search('\?field=(.+?)-(.*)', classes[0])
                if (tileClass):
                    field = tileClass.group(2)
                    talNode = etree.HTML('<' + tag + ' tal:content="item/'
                                     + field + '" ></' + tag + '>')
                    if (tileClass.group(2) == 'image'):
                        talNode = etree.HTML("""
                            <img tal:condition="python:item.getIcon"                          
                                 tal:attributes="src string:${item/getURL}/@@images/image/thumb"
                                 />""")
                    element.replace(
                        child, talNode.find('.//body/*'))
        else:
            replaceTiles(child)



def getBodyChilds(element):
    return element.find('./html/body/*')

@provider(IVocabularyFactory)
def availableListingViewsVocabulary(context):
    """Get available views for listing content as vocabulary"""
    registry = getUtility(IRegistry)
    listing_views = registry.get('plone.app.standardtiles.listing_views', {})
    if len(listing_views) == 0:
        listing_views = {
            'listing_view': u'Listing view',
            'summary_view': u'Summary view',
            'tabular_view': u'Tabular view'
        }
    voc = []
    for key, label in sorted(listing_views.items(), key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)

class ViewPageTemplateString(ViewPageTemplateFile):

    def __init__(self, text):
        super(ViewPageTemplateString, self).__init__(__file__)
        self.pt_edit(text, 'text/html')
        self._cook()

    def _cook_check(self):
        pass  # cooked only during init
