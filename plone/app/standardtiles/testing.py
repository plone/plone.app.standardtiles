# -*- coding: utf-8 -*-
from zope.configuration import xmlconfig
from plone.testing import z2
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting


class StandardTileLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import plone.app.standardtiles
        xmlconfig.file('configure.zcml', plone.app.standardtiles,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.standardtiles:default')


STANDARD_TILE_FIXTURE = StandardTileLayer()

STANDARD_TILE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(STANDARD_TILE_FIXTURE,),
    name="StandardTileLayer:Integration")
STANDARD_TILE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(STANDARD_TILE_FIXTURE,),
    name="StandardTileLayer:Functional")
STANDARD_TILE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(STANDARD_TILE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="StandardTileLayer:Acceptance")
