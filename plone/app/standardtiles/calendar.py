# -*- coding: utf-8 -*-
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from zope import schema
from plone.app.layout.calendar import CalendarMixin
from plone.app.vocabularies.catalog import CatalogSource


try:
    from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection as ICollection  # noqa
    from plone.app.contenttypes.interfaces import IFolder
    search_base_uid_source = CatalogSource(object_provides={
        'query': [
            ICollection.__identifier__,
            IFolder.__identifier__
        ],
        'operator': 'or'
    })
except ImportError:
    search_base_uid_source = CatalogSource(is_folderish=True)
    ICollection = None


class ICalendarTile(Schema):
    """Calendar tile schema interface."""

    state = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=None,
        required=False,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates")
    )

    search_base_uid = schema.Choice(
        title=_(u'portlet_label_search_base', default=u'Search base'),
        description=_(
            u'portlet_help_search_base',
            default=u'Select search base Folder or Collection to search for '
                    u'events. The URL to to this item will also be used to '
                    u'link to in calendar searches. If empty, the whole site '
                    u'will be searched and the event listing view will be '
                    u'called on the site root.'
        ),
        required=False,
        source=search_base_uid_source,
    )


class CalendarTile(CalendarMixin, Tile):
    """A tile displaying a calendar."""

    def __call__(self):
        self.setup()
        return self.index()
