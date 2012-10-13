# -*- coding: utf-8 -*-
from datetime import date
from zope.i18nmessageid import MessageFactory
from zope.schema import Text
from plone.tiles.tile import PersistentTile
from plone.supermodel import model
from plone.autoform import directives as form


_ = MessageFactory('plone')


class IFooterTile(model.Schema):

    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')

    text = Text(
        title=_("Tile text"),
        required=False
        )


class FooterTile(PersistentTile):
    """ A text tile """

    @property
    def actions(self):
        return [{
                'name': 'edit',
                'url': '@@edit-tile',
                'title': _('Edit'),
            }, {
                'name': 'remove',
                'url': '@@delete-tile',
                'title': _('Remove'),
            }]

    @property
    def year(self):
        return date.today().year
