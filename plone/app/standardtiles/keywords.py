# -*- coding: utf-8 -*-
import zope.deferredimport


zope.deferredimport.initialize()

# remove with 3.0

zope.deferredimport.deprecated(
    "Import from plone.app.standardtiles.common instead",
    KeywordsTile='plone.app.standardtiles.common:KeywordsTile',
)
