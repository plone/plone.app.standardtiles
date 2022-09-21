from plone.app.dexterity.behaviors.metadata import IDublinCore
from plone.app.standardtiles.utils import PermissionChecker
from plone.app.tiles.interfaces import ITilesFormLayer
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.autoform.view import WidgetsView
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from plone.formwidget.namedfile import NamedImageWidget
from plone.protect.interfaces import IDisableCSRFProtection
from plone.supermodel.utils import mergedTaggedValueDict
from plone.tiles import Tile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.browser.text import TextWidget
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.field import Fields
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from z3c.form.util import getSpecification
from zope.component import adapter
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.pagetemplate.interfaces import IPageTemplate


class IDexterityFieldTileFormOrGroup(Interface):
    """Marker interface for template overrides"""


@implementer(IDexterityFieldTileFormOrGroup)
@implementer(IAddForm)
@implementer(IEditForm)
class DexterityFieldTile(WidgetsView, Tile):
    """Field tile for Dexterity content."""

    _additionalSchemata = None

    @property
    def schema(self):
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        return fti.lookupSchema()

    @property
    def additionalSchemata(self):
        if self._additionalSchemata is not None:
            return iter(self._additionalSchemata)
        return getAdditionalSchemata(context=self.context)

    def __init__(self, context, request):
        # xxx usually a super is the way to go here? why not?
        Tile.__init__(self, context, request)
        WidgetsView.__init__(self, context, request)

        try:
            self.field = self.data["field"].split("-", 1)[-1]
        except KeyError:
            self.field = None
            return

        # Omit all the fields except rendered field to save time, because
        # autoform update will only add fields not in self.fields.

        if self.field in self.schema:
            self.fields = Fields(self.schema).omit(self.field)
        else:
            self.fields = Fields(self.schema).omit(self.schema.names())
            for schema in self.additionalSchemata:
                if self.field in schema:
                    self.field = f"{schema.__name__}.{self.field}"
                    self.fields += Fields(schema, prefix=schema.__name__).omit(
                        self.field
                    )
                    self._additionalSchemata = (schema,)
                    return

    @property
    def isVisible(self):
        """Checks wheter the user has read permission of the field: if this is
        not the case, then the field is not displayed
        """
        try:
            schema = next(self.additionalSchemata)
        except StopIteration:
            schema = self.schema

        return PermissionChecker(
            mergedTaggedValueDict(schema, READ_PERMISSIONS_KEY),
            self.context,
        ).allowed(self.field)

    def _wrap_widget(self, render):
        if render.rstrip().endswith("</html>"):
            return render
        return "".join(["<html><body>", render, "</body></html>"])

    def updateWidgets(self, prefix=None):
        if self.field is not None:

            if self.field in self.fields:
                self.fields = self.fields.select(self.field)
            else:
                self.fields = Fields()

            for group in self.groups or []:
                if self.field in group.fields:
                    group.fields = group.fields.select(self.field)
                else:
                    group.fields = Fields()

        super().updateWidgets(prefix)

    def __call__(self):
        if self.field and self.isVisible:
            self.update()

            widget = self.widgets.get(self.field)
            if widget is not None:
                return self._wrap_widget(widget.render())

            for group in self.groups:
                alsoProvides(group, IDexterityFieldTileFormOrGroup)
                widget = group.widgets.get(self.field)
                if widget is not None:
                    return self._wrap_widget(widget.render())
        return "<html></html>"


_titleDisplayTemplate = ViewPageTemplateFile(
    "templates/title.pt", content_type="text/html"
)
_descriptionDisplayTemplate = ViewPageTemplateFile(
    "templates/description.pt", content_type="text/html"
)
_namedImageDisplayTemplate = ViewPageTemplateFile(
    "templates/namedimage.pt", content_type="text/html"
)


@implementer(IPageTemplate)
@adapter(
    None,
    ITilesFormLayer,
    DexterityFieldTile,
    getSpecification(IDublinCore["title"]),
    TextWidget,
)
def titleDisplayTemplate(context, request, form, field, widget):
    return _titleDisplayTemplate


@implementer(IPageTemplate)
@adapter(
    None,
    ITilesFormLayer,
    DexterityFieldTile,
    getSpecification(IDublinCore["description"]),
    TextAreaWidget,
)
def descriptionDisplayTemplate(context, request, form, field, widget):
    return _descriptionDisplayTemplate


@implementer(IPageTemplate)
@adapter(None, ITilesFormLayer, IDexterityFieldTileFormOrGroup, None, NamedImageWidget)
def namedImageDisplayTemplate(context, request, form, field, widget):
    # Disable CSRF, because imagescales may save a new scale into ZODB
    alsoProvides(request, IDisableCSRFProtection)
    return _namedImageDisplayTemplate
