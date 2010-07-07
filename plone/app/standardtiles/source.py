from zope.component import getUtility

from zope.schema.vocabulary import SimpleTerm

from zope.intid.interfaces import IIntIds

from plone.formwidget.contenttree.source import PathSource
from plone.formwidget.contenttree.source import PathSourceBinder


class IntIdSource(PathSource):

    def _path_for_value(self, value):
        intids = getUtility(IIntIds)
        obj = intids.getObject(value)
        return '/'.join(obj.getPhysicalPath())

    def _term_for_brain(self, brain):
        path = brain.getPath()[len(self.portal_path):]
        obj = brain._unrestrictedGetObject()
        intids = getUtility(IIntIds)
        intid = intids.getId(obj)
        return SimpleTerm(intid,
                          path,
                          brain.Title)
        

class IntIdSourceBinder(PathSourceBinder):
    path_source = IntIdSource
