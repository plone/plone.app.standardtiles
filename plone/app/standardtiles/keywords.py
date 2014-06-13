# -*- coding: utf-8 -*-
from plone.app.standardtiles.utils import getNavigationRoot
from plone.tiles import PersistentTile
from urllib import quote


class KeywordsTile(PersistentTile):
    """A tile that displays the context's keywords, if any."""

    @property
    def categories(self):
        """Return context's categories."""

        return self.context.Subject()

    def catUrl(self, category):
        """Safely quote URL."""

        return "%s/search?Subject:list=%s" % \
               (getNavigationRoot(self.context).absolute_url(),
                quote(category))
