# -*- coding: utf-8 -*-
from zope.component import getUtility

from zope.schema.vocabulary import SimpleTerm

from zope.intid.interfaces import IIntIds

from plone.formwidget.contenttree.source import PathSource
from plone.formwidget.contenttree.source import PathSourceBinder


class IntIdSource(PathSource):

    def __init__(self, *args, **kwargs):
        self.intids = getUtility(IIntIds)
        super(IntIdSource, self).__init__(*args, **kwargs)

    def _path_for_value(self, value):
        obj = self.intids.getObject(value)
        return '/'.join(obj.getPhysicalPath())

    def _term_for_brain(self, brain, real_value=False):
        path = brain.getPath()[len(self.portal_path):]
        obj = brain._unrestrictedGetObject()

        intid = self.intids.getId(obj)
        return SimpleTerm(value=intid,
                          token=path,
                          title=brain.Title)


class IntIdSourceBinder(PathSourceBinder):
    path_source = IntIdSource
