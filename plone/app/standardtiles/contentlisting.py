from zope import schema
from zope.component import getMultiAdapter, queryMultiAdapter

from plone.app.contentlisting.interfaces import IContentListing
from plone.directives import form as directivesform
from plone.tiles import PersistentTile

from plone.formwidget.query.widget import QueryWidgetFieldWidget


class IContentListingTile(directivesform.Schema):
    """Video tile
    """
    directivesform.widget(search_terms=QueryWidgetFieldWidget)
    search_terms = schema.TextLine(title=u'Search terms',
                          description=u'Define the search terms for the items '
                          'you want to list by choosing what to match on. The '
                          'list of results will be dynamically updated')
    view_template = schema.Choice(title=u"Display mode",
                                  values=('tabular', 'summary'),
                                  required=True)


class ContentListingTile(PersistentTile):
    """ A tile that displays the content in a folderish item """

    def __call__(self):
        self.update()
        #return self.folderlisting.render()
        return self.index()

    def update(self):
        self.folderlisting = self.context.restrictedTraverse('@@folderListing')()
