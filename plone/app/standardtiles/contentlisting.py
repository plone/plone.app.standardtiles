# -*- coding: utf-8 -*-
# from plone.app.standardtiles.interfaces import IStandardTilesSettings
# from plone.registry.interfaces import IRegistry
# from zope.component import getUtility
from Products.CMFCore.interfaces import IFolderish
from plone.app.standardtiles import PloneMessageFactory as _
from plone.autoform.directives import widget
from plone.supermodel.model import Schema
from plone.tiles import Tile
from z3c.form.interfaces import IValue
from z3c.form.util import getSpecification
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

try:
    from plone.app.z3cform.widget import QueryStringFieldWidget
except ImportError:
    try:
        from plone.app.widgets.dx import QueryStringFieldWidget
    except ImportError:
        from z3c.form.interfaces import IFieldWidget
        from z3c.form.widget import FieldWidget
        from plone.app.widgets.dx import QueryStringWidget
        @implementer(IFieldWidget)
        def QueryStringFieldWidget(field, request):
                    return FieldWidget(field, QueryStringWidget(request))


class IContentListingTile(Schema):
    """A tile that displays a listing of content items"""
    widget(query=QueryStringFieldWidget)
    query = schema.List(
        title=_(u"Search terms"),
        value_type=schema.Dict(value_type=schema.Field(),
                               key_type=schema.TextLine()),
        description=_(u"Define the search terms for the items "
                      u"you want to list by choosing what to match on. The "
                      u"list of results will be dynamically updated"),
        required=False
    )

    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'Sort on'),
        description=_(u"Sort the collection on this index"),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_(u'label_sort_reversed', default=u'Reversed order'),
        description=_(u'Sort the results in reversed order'),
        required=False,
    )

    view_template = schema.Choice(title=_(u"Display mode"),
                                  source=_(u"Available Listing Views"),
                                  required=True)


class IContentListingTileLayer(Interface):
    """Layer (request marker interface) for content listing tile views"""


@implementer(IValue)
@adapter(None, None, None, getSpecification(IContentListingTile['query']), None)  # noqa
class DefaultQuery(object):
    def __init__(self, context, request, form, field, widget):
        self.context = context

    def get(self):
        if IFolderish.providedBy(self.context):
            return [{
                'i': 'path',
                'o': 'plone.app.querystring.operation.string.relativePath',
                'v': '::1'
            }]
        else:
            return [{
                'i': 'path',
                'o': 'plone.app.querystring.operation.string.relativePath',
                'v': '..::1'
            }]


@implementer(IValue)
@adapter(None, None, None, getSpecification(IContentListingTile['sort_on']), None)  # noqa
class DefaultSortOn(object):
    def __init__(self, context, request, form, field, widget):
        pass

    def get(self):
        return 'getObjPositionInParent'


class ContentListingTile(Tile):
    """A tile that displays a listing of content items"""

    def __call__(self):
        self.update()
        return self.contents()

    def update(self):
        self.query = self.data.get('query')
        if self.data.get('sort_reversed'):
            self.sort_order = 'reverse'
        else:
            self.sort_order = 'ascending'
        self.sort_on = self.data.get('sort_on')
        self.view_template = self.data.get('view_template')

    def contents(self):
        """Search results"""
        builder = getMultiAdapter((self.context, self.request),
                                  name='querybuilderresults')
        accessor = builder(query=self.query or [],
                           sort_on=self.sort_on or 'getObjPositionInParent',
                           sort_order=self.sort_order)
        view = self.view_template or 'listing_view'
        view = view.encode('utf-8')
        options = dict(original_context=self.context)
        alsoProvides(self.request, IContentListingTileLayer)
        return getMultiAdapter((accessor, self.request), name=view)(**options)


def availableListingViewsVocabulary(context):
    """Get available views for listing content as vocabulary"""
    # TODO: listing_views should be stored in a registry somehow
    listing_views = {
        'listing_view': u'Listing view',
        'summary_view': u'Summary view',
        'tabular_view': u'Tabular view'
    }
    # registry = getUtility(IRegistry)
    # proxy = registry.forInterface(IStandardTilesSettings)
    # sorted = proxy.listing_views.items()
    sorted = listing_views.items()
    sorted.sort(lambda a, b: cmp(a[1], b[1]))
    voc = []
    for key, label in sorted:
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)

directlyProvides(availableListingViewsVocabulary, IVocabularyFactory)

# XXX There used to be registry settings for plone.app.standardtiles:
#
# class IStandardTilesSettings(Interface):
#     """Settings for standard tiles."""
#     listing_views = schema.Dict(title=_(u"Listing views"),
#                                 description=_(u"Listing views available for "
#                                                "the content listing tile"),
#                                 key_type=schema.TextLine(),
#                                 value_type=schema.TextLine())
#
# <record interface="plone.app.standardtiles.interfaces.IStandardTilesSettings"
#         field="listing_views">
#   <value>
#       <element key="listing_view">Listing view</element>
#       <element key="summary_view">Summary view</element>
#       <element key="tabular_view">Tabular view</element>
#   </value>
# </record>
