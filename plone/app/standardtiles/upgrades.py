from Products.CMFCore.utils import getToolByName


PROFILE_ID = 'profile-plone.app.standardtiles:default'


def upgrade_registry(context, logger=None):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')