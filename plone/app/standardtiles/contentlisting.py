# -*- coding: utf-8 -*-
from operator import itemgetter
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.z3cform.widget import QueryStringFieldWidget
from plone.autoform.directives import widget
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from plone.tiles import Tile
from plone.tiles.interfaces import ITileType
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.utils import get_top_request
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
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

    title = schema.TextLine(title=_(u"label_title", default=u"Title"), required=False)

    description = schema.Text(
        title=_(u"label_description", default=u"Summary"),
        description=_(
            u"help_description", default=u"Used in item listings and search results."
        ),
        required=False,
        missing_value=u"",
    )

    use_context_query = schema.Bool(
        title=_(
            u"label_use_context_query", default=u"Use query parameters from content"
        ),
        description=_(
            u"If your content is a collection you can use the already existing listing configuration."
        ),
        required=False,
    )

    widget(query=QueryStringFieldWidget)
    query = schema.List(
        title=_(u"Search terms"),
        value_type=schema.Dict(value_type=schema.Field(), key_type=schema.TextLine()),
        description=_(
            u"Define the search terms for the items "
            u"you want to list by choosing what to match on. The "
            u"list of results will be dynamically updated"
        ),
        required=False,
    )

    ignore_request_params = schema.Bool(
        title=_(
            u"label_ignore_request_params",
            default=u"Ignore query parameters from request",
        ),
        description=_(
            u"Check this box if you do not want the results changed based on request parameters."
        ),
        required=False,
        default=False,
    )

    sort_on = schema.TextLine(
        title=_(u"label_sort_on", default=u"Sort on"),
        description=_(u"Sort the collection on this index"),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_(u"label_sort_reversed", default=u"Reversed order"),
        description=_(u"Sort the results in reversed order"),
        required=False,
    )

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Limit Search Results"),
        required=False,
        default=100,
        min=1,
    )

    item_count = schema.Int(
        title=_(u"label_item_count", default=u"Item count"),
        description=_(u"Number of items that will show up in one batch."),
        required=False,
        default=30,
        min=1,
    )

    tile_class = schema.TextLine(
        title=_(u"Tile additional styles"),
        description=_(
            u"Insert a list of additional CSS classes that will"
            + u" be added to the tile"
        ),
        default=u"",
        required=False,
    )

    view_template = schema.Choice(
        title=_(u"Display mode"), source=_(u"Available Listing Views"), required=True
    )


class IContentListingTileLayer(Interface):
    """Layer (request marker interface) for content listing tile views"""


@implementer(IValue)
@adapter(None, None, None, getSpecification(IContentListingTile["query"]), None)
class DefaultQuery(object):
    def __init__(self, context, request, form, field, widget):
        self.context = context

    def get(self):
        if IFolderish.providedBy(self.context):
            value = "::1"
        else:
            value = "..::1"
        return [
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.relativePath",
                "v": value,
            }
        ]


@implementer(IValue)
@adapter(None, None, None, getSpecification(IContentListingTile["sort_on"]), None)
class DefaultSortOn(object):
    def __init__(self, context, request, form, field, widget):
        pass

    def get(self):
        return "getObjPositionInParent"


class ContentListingTile(Tile):
    """A tile that displays a listing of content items"""

    template = ViewPageTemplateFile("templates/contentlisting_view.pt")

    def __call__(self):
        self.update()
        return self.template()

    def update(self):
        request = get_top_request(self.request)
        self.query = self.data.get("query")
        self.sort_on = self.data.get("sort_on")
        self.sort_order = (
            "reverse" if self.data.get("sort_reversed") else "ascending"
        )  # noqa: E501
        self.limit = self.data.get("limit")
        self.item_count = self.data.get("item_count")
        self.ignore_request_params = self.data.get("ignore_request_params")

        # use our custom b_start_str to enable multiple
        # batchings on one context
        self.b_start_str = "{}-b_start".format(self.id)
        self.b_start = int(request.get(self.b_start_str, 0))
        # batch url manipulation to original_context
        self.request["ACTUAL_URL"] = self.context.absolute_url()

        if self.data.get(
            "use_context_query", None
        ) and ISyndicatableCollection.providedBy(
            self.context
        ):  # noqa: E501
            self.query = self.context.query
            self.sort_on = self.context.sort_on
            self.sort_order = (
                "reverse" if self.context.sort_reversed else "ascending"
            )  # noqa: E501
            if not self.limit:
                self.limit = self.context.limit
            if not self.item_count:
                self.item_count = self.context.item_count

        if self.query is None or self.sort_on is None:
            # Get defaults
            tileType = queryUtility(ITileType, name=self.__name__)
            fields = getFields(tileType.schema)
            if self.query is None:
                self.query = getMultiAdapter(
                    (self.context, self.request, None, fields["query"], None),
                    name="default",
                ).get()
            if self.sort_on is None:
                self.sort_on = getMultiAdapter(
                    (self.context, self.request, None, fields["sort_on"], None),
                    name="default",
                ).get()

        self.view_template = self.data.get("view_template")

    @property
    def title(self):
        return self.data.get("title")

    @property
    def description(self):
        return self.data.get("description")

    def contents(self):
        """Search results"""
        builder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )

        # Include query parameters from request if not set to ignore
        contentFilter = {}
        if not self.ignore_request_params:
            contentFilter = dict(self.request.get("contentFilter", {}))

        accessor = builder(
            query=self.query,
            sort_on=self.sort_on or "getObjPositionInParent",
            sort_order=self.sort_order,
            limit=self.limit,
            batch=True,
            b_start=self.b_start,
            b_size=self.item_count or 30,
            brains=False,
            custom_query=contentFilter,
        )

        accessor.b_start_str = self.b_start_str

        view = self.view_template or "listing_view"
        options = dict(original_context=self.context)
        alsoProvides(self.request, IContentListingTileLayer)
        return getMultiAdapter((accessor, self.request), name=view)(**options)

    @property
    def tile_class(self):
        css_class = "contentlisting-tile"
        additional_classes = self.data.get("tile_class", "")
        if not additional_classes:
            return css_class
        return " ".join([css_class, additional_classes])


@provider(IVocabularyFactory)
def availableListingViewsVocabulary(context):
    """Get available views for listing content as vocabulary"""

    registry = getUtility(IRegistry)
    listing_views = registry.get("plone.app.standardtiles.listing_views", {})
    if len(listing_views) == 0:
        listing_views = {
            "listing_view": u"Listing view",
            "summary_view": u"Summary view",
            "tabular_view": u"Tabular view",
        }
    voc = []
    for key, label in sorted(listing_views.items(), key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)
