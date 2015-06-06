# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from plone.autoform import directives
from plone.dexterity.fti import DexterityFTI
from plone.portlets.interfaces import IPortletManager
from plone.portlets.manager import PortletManager
from plone.portlets.manager import PortletManagerRenderer
from plone.supermodel.model import Schema
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope import schema
from zope.component import adapter
from zope.component import adapts
from zope.component import getSiteManager
from zope.component import provideAdapter
from zope.configuration import xmlconfig
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implements
from zope.interface import implementsOnly
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView
import pkg_resources

HAS_PLONE_5 = \
    int(pkg_resources.get_distribution('Products.CMFPlone').version[0]) > 4

try:
    pkg_resources.get_distribution('plone.app.theming')
except pkg_resources.DistributionNotFound:
    HAS_PLONE_APP_THEMING = False
else:
    HAS_PLONE_APP_THEMING = True

NORMAL_USER_NAME = 'user'
NORMAL_USER_PASSWORD = 'secret'
EDITOR_USER_NAME = 'editor'
EDITOR_USER_PASSWORD = 'confidential'
MANAGER_USER_NAME = 'manager'
MANAGER_USER_PASSWORD = 'topsecret'


class RequestsGetMock(object):

    ok = True
    url = None

    def __init__(self, url):
        self.url = url

    def json(self):
        return {
            'html': u'<p>%s</p>' % self.url
        }


class IFunkyWidget(interfaces.IWidget):
    """Funky, useless widget for testing."""


class FunkyWidget(widget.HTMLTextInputWidget, Widget):
    """Funky widget implementation."""
    implementsOnly(IFunkyWidget)

    klass = u'funky-widget'
    value = u''

    def update(self):
        super(FunkyWidget, self).update()
        widget.addFieldClass(self)


@adapter(schema.interfaces.IField, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def FunkyFieldWidget(field, request):
    """IFieldWidget factory for FunkyWidget."""
    return FieldWidget(field, FunkyWidget(request))


class ITestType1(Schema):
    test_text = schema.TextLine(
        title=u"Test text field",
    )

    test_int = schema.Int(
        title=u"Integer test field",
    )

    test_bool = schema.Bool(
        title=u"Boolean test field",
    )

    directives.widget(
        funky=FunkyFieldWidget,
    )
    funky = schema.TextLine(
        title=u"Test funky field",
    )

    directives.read_permission(topsecret='cmf.ModifyPortalContent')
    directives.write_permission(topsecret='cmf.ManagePortal')
    topsecret = schema.TextLine(
        title=u"Top secret field",
    )


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

        import plone.app.widgets
        xmlconfig.file('configure.zcml', plone.app.widgets,
                       context=configurationContext)

        import plone.app.standardtiles
        xmlconfig.file('configure.zcml', plone.app.standardtiles,
                       context=configurationContext)

        import plone.app.standardtiles
        xmlconfig.file('testing.zcml', plone.app.standardtiles,
                       context=configurationContext)

        if HAS_PLONE_5:
            import plone.app.contenttypes
            xmlconfig.file('configure.zcml', plone.app.contenttypes,
                           context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.app.widgets:default')
        applyProfile(portal, 'plone.app.standardtiles:default')

        if HAS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')

        # ensure plone.app.theming disabled
        if HAS_PLONE_APP_THEMING:
            from plone.registry.interfaces import IRegistry
            from zope.component import getUtility
            registry = getUtility(IRegistry)
            key = 'plone.app.theming.interfaces.IThemeSettings.enabled'
            if key in registry:
                registry[key] = False

        # creates some users
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

        # register portlet manager and portlet manager renderer
        sm = getSiteManager(portal)
        sm.registerUtility(component=MockPortletManager(),
                           provided=IMockPortletManager,
                           name='mock.portletmanager')
        provideAdapter(MockPortletManagerRenderer)

        from plone.app.standardtiles import embed
        embed.requests.get = RequestsGetMock


class PAStandardtilesTestType(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import plone.app.dexterity
        xmlconfig.file('configure.zcml', plone.app.dexterity,
                       context=configurationContext)

        import plone.app.widgets
        xmlconfig.file('configure.zcml', plone.app.widgets,
                       context=configurationContext)

        import plone.app.standardtiles
        xmlconfig.file('configure.zcml', plone.app.standardtiles,
                       context=configurationContext)
        xmlconfig.file('testing.zcml', plone.app.standardtiles,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.app.widgets:default')
        applyProfile(portal, 'plone.app.standardtiles:default')

        # ensure plone.app.theming disabled
        if HAS_PLONE_APP_THEMING:
            from plone.registry.interfaces import IRegistry
            from zope.component import getUtility
            registry = getUtility(IRegistry)
            key = 'plone.app.theming.interfaces.IThemeSettings.enabled'
            if key in registry:
                registry[key] = False

        # creates some users
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

        # define the dexterity "junk" type
        fti = DexterityFTI('DecoTestType1')
        fti.schema = u'plone.app.standardtiles.testing.ITestType1'
        fti.behaviors = ('plone.app.dexterity.behaviors.metadata.IDublinCore',)
        portal.portal_types._setObject('DecoTestType1', fti)

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
