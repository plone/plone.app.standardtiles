# -*- coding: utf-8 -*-


def clean_up_registry():
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility
    registry = getUtility(IRegistry)

    records = [
        'plone.app.portlets.PortletManagerBlacklist',
        'plone.app.tiles',
    ]
    for r in records:
        values = list(registry[r])
        for v in values:
            if v.startswith('plone.app.standardtiles'):
                registry[r].remove(v)


def uninstall(portal, reinstall=False):
    from Products.CMFCore.utils import getToolByName
    if not reinstall:
        clean_up_registry()
        profile = 'profile-plone.app.standardtiles:uninstall'
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile(profile)
        return 'Ran all uninstall steps.'
