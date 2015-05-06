# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.testing.layers import IntegrationTesting
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import logout
from plone.dexterity.fti import DexterityFTI
from plone.portlets.interfaces import IPortletManager
from plone.portlets.manager import PortletManager
from plone.portlets.manager import PortletManagerRenderer
from zope.component import adapts
from zope.component import getSiteManager
from zope.component import provideAdapter
from zope.configuration import xmlconfig
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.interface import Interface
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView

NORMAL_USER_NAME = 'user'
NORMAL_USER_PASSWORD = 'secret'
EDITOR_USER_NAME = 'editor'
EDITOR_USER_PASSWORD = 'confidential'
MANAGER_USER_NAME = 'manager'
MANAGER_USER_PASSWORD = 'topsecret'


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
        import plone.app.dexterity
        xmlconfig.file('configure.zcml', plone.app.dexterity,
                       context=configurationContext)

        import plone.app.standardtiles
        xmlconfig.file('configure.zcml', plone.app.standardtiles,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.app.standardtiles:default')

        # register portlet manager and portlet manager renderer
        sm = getSiteManager(portal)
        sm.registerUtility(component=MockPortletManager(),
                           provided=IMockPortletManager,
                           name='mock.portletmanager')
        provideAdapter(MockPortletManagerRenderer)


class PAStandardtilesTestType(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import plone.app.standardtiles
        xmlconfig.file('testing.zcml', plone.app.standardtiles,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.app.standardtiles:default')

        # Creates some users
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser(
            NORMAL_USER_NAME,
            NORMAL_USER_PASSWORD,
            ['Member'],
            [],
        )
        acl_users.userFolderAddUser(
            EDITOR_USER_NAME,
            EDITOR_USER_PASSWORD,
            ['Editor'],
            [],
        )
        acl_users.userFolderAddUser(
            MANAGER_USER_NAME,
            MANAGER_USER_PASSWORD,
            ['Manager'],
            [],
        )

        # Define the dexterity "junk" type
        fti = DexterityFTI('DecoTestType1')
        fti.schema = u'plone.app.standardtiles.testing.ITestType1'
        fti.behaviors = ('plone.app.dexterity.behaviors.metadata.IDublinCore',)
        portal.portal_types._setObject('DecoTestType1', fti)
        schema = fti.lookupSchema()

        # inserts the content of the types defined above
        login(portal, MANAGER_USER_NAME)
        content = portal[portal.invokeFactory('DecoTestType1',
                                              'deco-test-type1')]
        content.title = u"Test content"
        content.description = u"Just a test content"
        content.contributors = (u'Jane Doe', u'John Doe')
        logout()


PASTANDARDTILES_FIXTURE = PAStandardtiles()
PASTANDARDTILES_TESTTYPE_FIXTURE = PAStandardtilesTestType()

PASTANDARDTILES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PASTANDARDTILES_FIXTURE,), name="PAStandardTiles:Integration")
PASTANDARDTILES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PASTANDARDTILES_FIXTURE,), name="PAStandardTiles:Functional")
PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PASTANDARDTILES_TESTTYPE_FIXTURE,),
    name="PAStandardTilesTestType:Functional",
)
