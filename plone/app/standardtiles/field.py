# -*- coding: utf-8 -*-
from plone.app.standardtiles.utils import PermissionChecker
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.browser.view import DefaultView
from plone.supermodel.utils import mergedTaggedValueDict
from plone.tiles import Tile
from plone.z3cform import z2
from z3c.form.field import Fields


class DexterityFieldTile(DefaultView, Tile):
    """Field tile for Dexterity content."""

    behavior_schema = None
    behavior_field = None

    def __init__(self, context, request):
        Tile.__init__(self, context, request)
        DefaultView.__init__(self, context, request)

        try:
            components = self.data['field'].split('-', 1)
            self.field = components[-1]
        except KeyError:
            self.field = None

        if self.field is not None and self.field in self.schema:
            self.fields = Fields(self.schema).select(self.field)

        elif self.field is not None:
            for schema in self.additionalSchemata:
                if self.field in schema:
                    self.fields = Fields(schema).select(self.field)
                    self.behavior_schema = schema
                    self.behavior_field = '%s.%s' % (schema.__name__, self.field)  # noqa
                    break

    @property
    def isVisible(self):
        """Checks wheter the user has read permission of the field: if this is
        not the case, then the field is not displayed
        """
        return PermissionChecker(
            mergedTaggedValueDict(self.behavior_schema or self.schema,
                                  READ_PERMISSIONS_KEY),
            self.context,
        ).allowed(self.field)

    def _wrap_widget(self, render):
        return u"<html><body>%s</body></html>" % render

    def __call__(self):
        z2.switch_on(self)
        if self.field and self.isVisible:
            self.update()
            widget = self.widgets.get(self.behavior_field,
                                      self.widgets.get(self.field))
            return self._wrap_widget(widget.render())
        else:
            return self._wrap_widget(u'')
