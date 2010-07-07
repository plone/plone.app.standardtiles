from Acquisition import aq_chain, aq_inner
from plone.app.layout.navigation.interfaces import INavigationRoot


def getNavigationRoot(context):
    for obj in aq_chain(aq_inner(context)):
        if INavigationRoot.providedBy(obj):
            break
    return obj
