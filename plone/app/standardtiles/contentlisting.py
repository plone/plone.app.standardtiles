from zope import schema
from zope.component import getMultiAdapter
from plone.directives import form as directivesform
from plone.tiles import PersistentTile
from plone.formwidget.querystring.widget import QueryStringFieldWidget
from plone.app.collection import queryparser


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
                                  values=('tabular', 'summary'),
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
        view = 'collection_%s_view' % self.view_template

        view = 'display_query_results'
        return getMultiAdapter((accessor, self.request), name=view)()
