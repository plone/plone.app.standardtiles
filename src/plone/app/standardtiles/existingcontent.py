from Acquisition import aq_parent
from operator import itemgetter
from plone import api
from plone.app.blocks import utils
from plone.app.blocks.tiles import renderTiles
from plone.app.standardtiles import PloneMessageFactory as _
from plone.autoform import directives as form
from plone.base.utils import safe_text
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from plone.tiles import Tile
from plone.uuid.interfaces import IUUID
from repoze.xmliter.utils import getHTMLSerializer
from z3c.form import validator
from zExceptions import Unauthorized
from ZODB.POSException import POSKeyError
from zope import schema
from zope.browser.interfaces import IBrowserView
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Invalid
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

import copy


try:
    from plone.app.z3cform.widgets.contentbrowser import (
        ContentBrowserFieldWidget as ExistingContentBrowserWidget,
    )
except ImportError:
    # fallback for Plone 6.0
    from plone.app.z3cform.widgets.relateditems import (
        RelatedItemsFieldWidget as ExistingContentBrowserWidget,
    )

try:
    from plone.app.discussion.interfaces import IConversation
except ImportError:
    # plone.app.discussion is optional since Plone 6.1.
    IConversation = None


def uuidToObject(uuid):
    """Given a UUID, attempt to return a content object. Will return
    None if the UUID can't be found. Raises Unauthorized if the current
    user is not allowed to access the object.
    """

    brain = uuidToCatalogBrainUnrestricted(uuid)
    if brain is None:
        return

    return brain.getObject()


def uuidToCatalogBrainUnrestricted(uuid):
    """Given a UUID, attempt to return a catalog brain even when the object is
    not visible for the logged in user (e.g. during anonymous traversal)
    """

    site = getSite()
    if site is None:
        return

    catalog = api.portal.get_tool("portal_catalog")
    if catalog is None:
        return

    result = catalog.unrestrictedSearchResults(UID=uuid)
    if len(result) != 1:
        return

    return result[0]


class IExistingContentTile(model.Schema):
    content_uid = schema.Choice(
        title=_("Select an existing content"),
        required=True,
        vocabulary="plone.app.vocabularies.Catalog",
    )
    form.widget(
        "content_uid",
        ExistingContentBrowserWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={"recentlyUsed": True},
    )

    show_title = schema.Bool(
        title=_("Show content title"),
        default=True,
        required=False,
    )

    show_description = schema.Bool(
        title=_("Show content description"),
        default=True,
        required=False,
    )

    show_text = schema.Bool(
        title=_("Show content text"),
        default=True,
        required=False,
    )

    show_image = schema.Bool(
        title=_("Show content image (if available)"),
        default=False,
        required=False,
    )

    image_scale = schema.Choice(
        title=_("Image scale"),
        vocabulary="plone.app.vocabularies.ImagesScales",
        required=False,
    )

    show_comments = schema.Bool(
        title=_("Show content comments count (if enabled)"),
        default=False,
        required=False,
    )

    tile_class = schema.TextLine(
        title=_("Tile additional styles"),
        description=_(
            "Insert a list of additional CSS classes that will"
            + " be added to the tile"
        ),
        default="",
        required=False,
    )

    view_template = schema.Choice(
        title=_("Display mode"),
        source="Available Content Views",
        required=True,
    )


class SameContentValidator(validator.SimpleFieldValidator):
    def validate(self, content_uid):
        super().validate(content_uid)
        context = aq_parent(self.context)  # default context is tile data
        if content_uid and IUUID(context, None) == content_uid:
            raise Invalid(
                "You can not select the same content as the page you are "
                "currently on."
            )


# Register validator
validator.WidgetValidatorDiscriminators(
    SameContentValidator, field=IExistingContentTile["content_uid"]
)


class ExistingContentTile(Tile):
    """Existing content tile"""

    @property
    @memoize
    def content_context(self):
        uuid = self.data.get("content_uid")
        if uuid != IUUID(self.context, None):
            try:
                item = uuidToObject(uuid)
            except Unauthorized:
                item = None
            if item is not None:
                return item

    @property
    @memoize
    def content_view(self):
        context = self.content_context
        if context is not None:
            try:
                return api.content.get_view(
                    name=self.content_view_name, context=context, request=self.request
                )
            except api.exc.InvalidParameterError:
                # view is not yet created
                pass

    @property
    def content_view_name(self):
        context = self.content_context
        if context is not None:
            # note: "view_template" is None during tests with missing parameter
            if self.data.get("view_template") in ["default_layout", None]:
                return context.getLayout()
            else:
                return self.data.get("view_template")
        return ""

    _marker = dict()

    @property
    def item_macros(self):
        view = self.content_view
        if view and IBrowserView.providedBy(view):
            # IBrowserView
            if getattr(view, "index", None):
                macros = getattr(view.index, "macros", self._marker)
                if macros is not self._marker:
                    return view.index.macros
        elif view:
            # FSPageTemplate
            return view.macros

    @property
    def item_panels(self):
        content_view = self.content_view

        if content_view is None:
            return []

        html = content_view()
        if isinstance(html, str):
            html = html.encode("utf-8")
        serializer = getHTMLSerializer([html], pretty_print=False, encoding="utf-8")
        panels = [node for node in utils.panelXPath(serializer.tree)]
        if panels:
            request = self.request.clone()
            request.URL = self.content_context.absolute_url() + "/"
            try:
                renderTiles(request, serializer.tree)
            except RuntimeError:  # maximum recursion depth exceeded
                return []
            clear = '<div style="clear: both;"></div>'

            result = []
            serializer = serializer.serializer
            for panel in panels:
                panel_html = []
                for child in panel.getchildren():
                    # lxml element needs to be copied
                    # to put it out of context of the root tree it comes from.
                    # If this is not done, serializer will keep on serializing
                    # after element is closed until last
                    # element of the root tree.
                    child_copy = copy.deepcopy(child)
                    child_html = safe_text(serializer(child_copy))
                    panel_html.append(child_html)
                panel_html = "".join(panel_html)
                result.append(panel_html)
            result.append(clear)
            return result

        return []

    @property
    def image_tag(self):
        context = self.content_context
        if not context:
            return ""
        try:
            scale_view = api.content.get_view(
                name="images", context=context, request=self.request
            )
            scale = self.data.get("image_scale", "thumb")
            return scale_view.scale("image", scale=scale).tag()
        except (api.exc.InvalidParameterError, POSKeyError, AttributeError):
            # The object doesn't have an image field
            return ""

    @property
    def comments_count(self):
        if IConversation is None:
            return 0
        context = self.content_context
        try:
            conversation = IConversation(context)
        except Exception:
            return 0
        return conversation.total_comments()

    @property
    def tile_class(self):
        css_class = "existing-content-tile"
        additional_classes = self.data.get("tile_class", "")
        if not additional_classes:
            return css_class
        return " ".join([css_class, additional_classes])


@provider(IVocabularyFactory)
def availableContentViewsVocabulary(context):
    """Get available views for a content as vocabulary"""

    registry = getUtility(IRegistry)
    listing_views = registry.get("plone.app.standardtiles.content_views", {}) or {}
    voc = [
        SimpleVocabulary.createTerm("default_layout", "default_layout", "Default view")
    ]
    for key, label in sorted(listing_views.items(), key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)
