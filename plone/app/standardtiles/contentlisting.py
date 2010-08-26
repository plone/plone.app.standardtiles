from zope import schema
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter

from plone.directives import form as directivesform
from plone.tiles import PersistentTile

from plone.app.collection.browser.querybuilder import QueryBuilder

from plone.formwidget.querystring.widget import QueryStringFieldWidget
from plone.formwidget.querystring import field


class IContentListingTile(directivesform.Schema):
    """ A tile that displays the content in a folderish item """
    directivesform.widget(query=QueryStringFieldWidget)
    query = schema.List(title=u'Search terms',
                        value_type=schema.Dict(value_type=schema.TextLine(), key_type=schema.TextLine()),
                        description=u'Define the search terms for the items '
                        'you want to list by choosing what to match on. The '
                        'list of results will be dynamically updated',
                        required=False)
    view_template = schema.Choice(title=u"Display mode",
                                  values=('tabular', 'summary'),
                                  required=True)


class ContentListingTile(PersistentTile):
    """ A tile that displays the content in a folderish item """

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.query = self.data.get('query')

    def SearchResults(self):
        """search results"""
        
        return getMultiAdapter((self.query, self.request), name='display_query_results')()
