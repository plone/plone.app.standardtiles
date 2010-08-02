from z3c.form.form import DisplayForm
from z3c.form.field import Fields
from plone.dexterity.utils import iterSchemata
from plone.tiles import Tile
from plone.supermodel.utils import mergedTaggedValueDict
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.utils import resolveDottedName
from plone.z3cform import z2


class DexterityFieldTile(DisplayForm, Tile):
    """Field tile for Dexterity content
    """

    def __init__(self, context, request):
        Tile.__init__(self, context, request)
        DisplayForm.__init__(self, context, request)
        self.fields = Fields(*iterSchemata(self.context))

    def updateWidgets(self):
        for schema in iterSchemata(self.context):
            widgets = mergedTaggedValueDict(schema, WIDGETS_KEY)
            for name, factory in widgets.items():
                if self.fields[name].widgetFactory.get(self.mode, None) is None:
                    if isinstance(factory, basestring):
                        factory = resolveDottedName(factory)
                    self.fields[name].widgetFactory = factory
        DisplayForm.updateWidgets(self)

    def _wrap_widget(self, render):
        return u"<html><body>%s</body></html>" % render

    def __call__(self):
        z2.switch_on(self)
        self.update()
        return self._wrap_widget(self.widgets[self.data['field']].render())
