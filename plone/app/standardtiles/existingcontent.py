# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from operator import itemgetter
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.blocks import utils
from plone.app.blocks.tiles import renderTiles
from plone.app.discussion.interfaces import IConversation
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from plone.tiles import Tile
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
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

import six


def uuidToObject(uuid):
    """Given a UUID, attempt to return a content object. Will return
    None if the UUID can't be found. Raises Unauthorized if the current
    user is not allowed to access the object.
    """

    brain = uuidToCatalogBrainUnrestricted(uuid)
    if brain is None:
        return None

    return brain.getObject()


def uuidToCatalogBrainUnrestricted(uuid):
    """Given a UUID, attempt to return a catalog brain even when the object is
    not visible for the logged in user (e.g. during anonymous traversal)
    """

    site = getSite()
    if site is None:
        return None

    catalog = api.portal.get_tool("portal_catalog")
    if catalog is None:
        return None

    result = catalog.unrestrictedSearchResults(UID=uuid)
    if len(result) != 1:
        return None

    return result[0]


class IExistingContentTile(model.Schema):

    content_uid = schema.Choice(
        title=_(u"Select an existing content"),
        required=True,
        vocabulary="plone.app.vocabularies.Catalog",
    )
    form.widget(
        "content_uid",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={"recentlyUsed": True},
    )

    show_title = schema.Bool(title=_(u"Show content title"), default=True)

    show_description = schema.Bool(title=_(u"Show content description"), default=True)

    show_text = schema.Bool(title=_(u"Show content text"), default=True)

    show_image = schema.Bool(
        title=_(u"Show content image (if available)"),
        default=False,
        required=False,
    )

    image_scale = schema.Choice(
        title=_(u"Image scale"),
        vocabulary="plone.app.vocabularies.ImagesScales",
        required=False,
    )

    show_comments = schema.Bool(
        title=_(u"Show content comments count (if enabled)"),
        default=False,
        required=False,
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
        title=_(u"Display mode"),
        source=_(u"Available Content Views"),
        required=True,
    )


class SameContentValidator(validator.SimpleFieldValidator):
    def validate(self, content_uid):
        super(SameContentValidator, self).validate(content_uid)
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
                if not self.request.get("PUBLISHED") and six.PY2:
                    # XXX: This reraise behaves strange in Python 3
                    # while in Py2 the traversal continues Py3 gets stuck
                    # in AccessControl.unauthorized.Unauthorized exception.
                    raise  # Should raise while still traversing
            if item is not None:
                return item
        return None

    @property
    @memoize
    def content_view(self):
        context = self.content_context
        if context is not None:
            view_name = self.data.get("view_template") or context.getLayout()
            return api.content.get_view(
                name=view_name, context=context, request=self.request
            )
        return None

    @property
    def item_macros(self):
        view = self.content_view
        if view and IBrowserView.providedBy(view):
            # IBrowserView
            if getattr(view, "index", None):
                return view.index.macros
        elif view:
            # FSPageTemplate
            return view.macros
        return None

    @property
    def item_panels(self):
        content_view = self.content_view
        html = content_view()
        if isinstance(html, six.text_type):
            html = html.encode("utf-8")
        serializer = getHTMLSerializer([html], pretty_print=False, encoding="utf-8")
        panels = dict(
            (node.attrib["data-panel"], node)
            for node in utils.panelXPath(serializer.tree)
        )
        if panels:
            request = self.request.clone()
            request.URL = self.content_context.absolute_url() + "/"
            try:
                renderTiles(request, serializer.tree)
            except RuntimeError:  # maximum recursion depth exceeded
                return []
            clear = '<div style="clear: both;"></div>'
            return [
                "".join(
                    [
                        safe_unicode(serializer.serializer(child))
                        for child in node.getchildren()
                    ]
                )
                for name, node in panels.items()
            ] + [clear]
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
        except (InvalidParameterError, POSKeyError, AttributeError):
            # The object doesn't have an image field
            return ""

    @property
    def comments_count(self):
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

    def __getattr__(self, name):
        # proxy attributes for this view to the selected view of the content
        # item so views work
        if (
            name
            in (
                "data",
                "content_context",
                "content_view",
                "item_macros",
                "item_panels",
                "getPhysicalPath",
                "index_html",
            )
            or name.startswith(("_", "im_", "func_"))
        ):
            return Tile.__getattr__(self, name)
        return getattr(self.content_view, name)


@provider(IVocabularyFactory)
def availableContentViewsVocabulary(context):
    """Get available views for a content as vocabulary"""

    registry = getUtility(IRegistry)
    listing_views = registry.get("plone.app.standardtiles.content_views", {}) or {}
    voc = [SimpleVocabulary.createTerm("", "", "Default view")]
    for key, label in sorted(listing_views.items(), key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)
