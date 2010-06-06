from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from z3c.form.interfaces import IFieldWidget, IContextAware, DISPLAY_MODE
from plone.dexterity.utils import iterSchemata
from plone.tiles import Tile
from plone.supermodel.utils import mergedTaggedValueDict
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.utils import resolveDottedName


class DexterityFieldTile(Tile):
    """Field tile for Dexterity content
    """

    def _wrap_widget(self, render):
        return u"<html><body>%s</body></html>" % render
    
    def __call__(self):
        for schema in iterSchemata(self.context):
            if self.data['field'] in schema:
                widgets = mergedTaggedValueDict(schema, WIDGETS_KEY)
                if self.data['field'] in widgets:
                    factory = widgets[self.data['field']]
                    if isinstance(factory, basestring):
                        factory = resolveDottedName(factory)
                    widget = factory(schema[self.data['field']], self.request)
                else:
                    widget = getMultiAdapter(
                        (schema[self.data['field']], self.request),
                        IFieldWidget
                    )
                if not IContextAware.providedBy(widget):
                    alsoProvides(widget, IContextAware)
                widget.mode = DISPLAY_MODE
                widget.context = self.context
                widget.update()
                return self._wrap_widget(widget.render())
        raise KeyError("Context '%s' does not have a field named '%s'" % (
            self.context,
            self.data['field']
        ))
