import unittest2 as unittest
import doctest
from plone.testing import layered

from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct

from zope.configuration import xmlconfig

from zope.interface import implements, Interface
from zope.component import adapts, provideAdapter, getSiteManager

from zope.publisher.interfaces.browser import IBrowserView, IBrowserRequest
from zope.contentprovider.interfaces import UpdateNotCalled

from plone.portlets.interfaces import IPortletManager
from plone.portlets.manager import PortletManager, PortletManagerRenderer


class IMockPortletManager(IPortletManager):
    """Marker interface for the mock portlet manager."""


class MockPortletManager(PortletManager):
    """Mock portlet manager to use in tests."""

    implements(IMockPortletManager)


class MockPortletManagerRenderer(PortletManagerRenderer):
    """Mock portlet manager renderer to use in tests."""

    adapts(Interface, IBrowserRequest, IBrowserView, IMockPortletManager)

    def __init__(self, context, request, view, manager):
        self.__updated = False

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        return "Portlet Manager Renderer output."


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

        # register portlet manager and portlet manager renderer
        sm = getSiteManager(portal)
        sm.registerUtility(component=MockPortletManager(),
                           provided=IMockPortletManager,
                           name='mock.portletmanager')
        provideAdapter(MockPortletManagerRenderer)

PASTANDARDTILES_INTEGRATION_TESTING = PAStandardtiles()
PASTANDARDTILES_FUNCTIONAL_TESTING = PAStandardtiles(bases=(PLONE_FUNCTIONAL_TESTING,))

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('standardtiles.txt', 
                                     optionflags=optionflags),
                layer=PASTANDARDTILES_FUNCTIONAL_TESTING)
        ])
    return suite
