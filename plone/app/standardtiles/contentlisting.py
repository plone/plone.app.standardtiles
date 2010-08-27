from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary
from plone.directives import form as directivesform
from plone.tiles import PersistentTile
from plone.formwidget.querystring.widget import QueryStringFieldWidget
from plone.app.collection import queryparser
from plone.registry.interfaces import IRegistry
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import directlyProvides
from plone.app.standardtiles.interfaces import IStandardTilesSettings


class IContentListingTile(directivesform.Schema):
    """ A tile that displays the content in a folderish item """
    directivesform.widget(query=QueryStringFieldWidget)
    query = schema.List(title=u'Search terms',
                        value_type=schema.Dict(value_type=schema.TextLine(),
                                               key_type=schema.TextLine()),
                        description=u'Define the search terms for the items '
                        'you want to list by choosing what to match on. The '
                        'list of results will be dynamically updated',
                        required=False)
    view_template = schema.Choice(title=u"Display mode",
                                  source=u"Available Listing Views",
                                  required=True)


class ContentListingTile(PersistentTile):
    """A tile that displays a listing of content items"""

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.query = self.data.get('query')
        self.view_template = self.data.get('view_template')

    def SearchResults(self):
        """search results"""
        parsedquery = queryparser.parseFormquery(self.context, self.query)
        accessor = getMultiAdapter((self.context, self.request),
            name='searchResults')(query=parsedquery)
        view = self.view_template
        view = view.encode('utf-8')
        return getMultiAdapter((accessor, self.request), name=view)()


def availableListingViewsVocabulary(context):
    """Get available views for listing content as vocabulary"""
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IStandardTilesSettings)
    sorted = proxy.listing_views.items()
    sorted.sort(lambda a, b: cmp(a[1], b[1]))
    voc = []

    for key, label in sorted:
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)

directlyProvides(availableListingViewsVocabulary, IVocabularyFactory)
