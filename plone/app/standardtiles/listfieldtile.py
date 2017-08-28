from operator import itemgetter
from plone import api
from plone.app.standardtiles import PloneMessageFactory as _
from plone.tiles import Tile
from plone.app.mosaic.browser.main_template import ViewPageTemplateString
from plone.supermodel.model import Schema
from plone.supermodel.directives import primary
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class IListFieldTile(Schema):
    primary('field')
    field = schema.Choice(
        title=_(u'Displayed field'),
        source=_(u'Available metadata fields'),
        required=False
    )

class ListFieldTile(Tile):

    @property
    def field(self):
        return self.data.get('field')

@provider(IVocabularyFactory)
def metadataFieldVocabulary(context):
    """Get available views for listing content as vocabulary"""
    catalog = api.portal.get_tool(name="portal_catalog")
    values = catalog.schema()
    voc = []
    for value in sorted(values, key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(value))
    return SimpleVocabulary(voc)
