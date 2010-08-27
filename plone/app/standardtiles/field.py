from z3c.form.form import DisplayForm
from z3c.form.field import Fields
from plone.dexterity.utils import iterSchemata
from plone.tiles import Tile
from plone.supermodel.utils import mergedTaggedValueDict
from plone.autoform.interfaces import WIDGETS_KEY, READ_PERMISSIONS_KEY
from plone.autoform.utils import _getDisallowedFields, resolveDottedName
from plone.z3cform import z2


class DexterityFieldTile(DisplayForm, Tile):
    """Field tile for Dexterity content
    """

    def __init__(self, context, request):
        Tile.__init__(self, context, request)
        DisplayForm.__init__(self, context, request)
        components = self.data['field'].split('-', 1)
        self.schema = None
        if len(components) > 1:
            for schema in iterSchemata(self.context):
                if schema.__identifier__.endswith(components[0]):
                    self.schema = schema
        else:
            self.schema = tuple(iterSchemata(self.context))[0]
        self.field = components[-1]
        self.fields = Fields(self.schema).select(self.field)

    def updateWidgets(self):
        widgets = mergedTaggedValueDict(self.schema, WIDGETS_KEY)
        if self.field in widgets:
            factory = widgets[self.field]
            if self.fields[self.field].widgetFactory.get(
                        self.mode, None) is None:
                if isinstance(factory, basestring):
                    factory = resolveDottedName(factory)
                self.fields[self.field].widgetFactory = factory
        DisplayForm.updateWidgets(self)

    @property
    def isVisible(self):
        """Checks wheter the user has read permission of the field: if this is
        not the case, then the field is not displayed
        """
        if self.field in _getDisallowedFields(
            self.context,
            mergedTaggedValueDict(self.schema, READ_PERMISSIONS_KEY),
            ''
        ):
            return False
        return True

    def _wrap_widget(self, render):
        return u"<html><body>%s</body></html>" % render

    def __call__(self):
        z2.switch_on(self)
        if self.isVisible:
            self.update()
            return self._wrap_widget(self.widgets[self.field].render())
        else:
            return self._wrap_widget(u'')
