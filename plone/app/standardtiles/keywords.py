from plone.tiles import PersistentTile
from urllib import quote
from plone.app.standardtiles.utils import getNavigationRoot


class KeywordsTile(PersistentTile):
    
    """ A tile that displays the context's keywords, if any """


    def __call__(self):
        self.update()
        return self.index()


    def update(self):
        pass


    @property
    def categories(self):

        """ Return context's categories """

        return self.context.Subject()


    def catUrl(self, category):

        """ Safely quote URL """
      
        return "%s/search?Subject:list=%s" % \
               (getNavigationRoot(self.context).absolute_url(), quote(category));
