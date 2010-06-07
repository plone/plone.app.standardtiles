import unittest2 as unittest
import doctest
from plone.testing import layered

from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct

from zope.configuration import xmlconfig


optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

class PAStandardtiles(PloneSandboxLayer):
    defaultBases = (PLONE_INTEGRATION_TESTING,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import plone.app.standardtiles
        xmlconfig.file('configure.zcml', plone.app.standardtiles,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        quickInstallProduct(portal, 'plone.app.standardtiles')


PASTANDARDTILES_INTEGRATION_TESTING = PAStandardtiles()
PASTANDARDTILES_FUNCTIONAL_TESTING = PAStandardtiles(bases=(PLONE_FUNCTIONAL_TESTING,))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('standardtiles.txt', 
                                     optionflags=optionflags),
                layer=PASTANDARDTILES_FUNCTIONAL_TESTING)
        ])
    return suite
