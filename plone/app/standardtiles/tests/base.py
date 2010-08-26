from plone.app.testing.layers import IntegrationTesting
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles

from zope.configuration import xmlconfig

from zope.interface import implements, Interface
from zope.component import adapts, provideAdapter, getSiteManager

from zope.publisher.interfaces.browser import IBrowserView, IBrowserRequest
from zope.contentprovider.interfaces import UpdateNotCalled

from plone.portlets.interfaces import IPortletManager
from plone.portlets.manager import PortletManager, PortletManagerRenderer

from plone.dexterity.fti import DexterityFTI


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
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import plone.app.standardtiles
        xmlconfig.file('configure.zcml', plone.app.standardtiles,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.app.intid:default')
        applyProfile(portal, 'plone.app.standardtiles:default')

        # register portlet manager and portlet manager renderer
        sm = getSiteManager(portal)
        sm.registerUtility(component=MockPortletManager(),
                           provided=IMockPortletManager,
                           name='mock.portletmanager')
        provideAdapter(MockPortletManagerRenderer)


class PAStandardtilesTestType(PAStandardtiles):

    def setUpPloneSite(self, portal):
        super(PAStandardtilesTestType, self).setUpPloneSite(portal)
        # Define the dexterity "junk" type
        fti = DexterityFTI('test_type')
        fti.behaviors = ('plone.app.dexterity.behaviors.metadata.IOwnership',)
        portal.portal_types._setObject('test_type', fti)
        schema = fti.lookupSchema()
        # inserts the content of the types defined above
        setRoles(portal, TEST_USER_NAME, ['Manager'])
        login(portal, TEST_USER_NAME)
        content = portal[portal.invokeFactory('test_type', 'test_type')]
        content.contributors = (u"jane doe", u"john doe")
        logout()


PASTANDARDTILES_FIXTURE = PAStandardtiles()
PASTANDARDTILES_TESTTYPE_FIXTURE = PAStandardtilesTestType()

PASTANDARDTILES_INTEGRATION_TESTING = IntegrationTesting(bases=(PASTANDARDTILES_FIXTURE,), name="PAStandardTiles:Integration")
PASTANDARDTILES_FUNCTIONAL_TESTING = FunctionalTesting(bases=(PASTANDARDTILES_FIXTURE,), name="PAStandardTiles:Functional")
PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PASTANDARDTILES_TESTTYPE_FIXTURE,),
    name="PAStandardTilesTestType:Functional"
)
