from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from plone.autoform import directives
from plone.dexterity.fti import DexterityFTI
from plone.portlets.interfaces import IPortletManager
from plone.portlets.manager import PortletManager
from plone.portlets.manager import PortletManagerRenderer
from plone.supermodel.model import Schema
from Products.CMFCore.utils import getToolByName
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope import schema
from zope.component import adapter
from zope.component import getSiteManager
from zope.component import provideAdapter
from zope.configuration import xmlconfig
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.interface import implementer
from zope.interface import implementer_only
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView


NORMAL_USER_NAME = "user"
NORMAL_USER_PASSWORD = "secret"
EDITOR_USER_NAME = "editor"
EDITOR_USER_PASSWORD = "confidential"
MANAGER_USER_NAME = "manager"
MANAGER_USER_PASSWORD = "topsecret"


class RequestsGetMock:

    ok = True
    url = None

    def __init__(self, url):
        self.url = url

    def json(self):
        return {"html": "<p>%s</p>" % self.url}


class IFunkyWidget(interfaces.IWidget):
    """Funky, useless widget for testing."""


@implementer_only(IFunkyWidget)
class FunkyWidget(widget.HTMLTextInputWidget, Widget):
    """Funky widget implementation."""

    klass = "funky-widget"
    value = ""

    def update(self):
        super().update()
        widget.addFieldClass(self)


@adapter(schema.interfaces.IField, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def FunkyFieldWidget(field, request):
    """IFieldWidget factory for FunkyWidget."""
    return FieldWidget(field, FunkyWidget(request))


class ITestType1(Schema):
    test_text = schema.TextLine(
        title="Test text field",
    )

    test_int = schema.Int(
        title="Integer test field",
    )

    test_bool = schema.Bool(
        title="Boolean test field",
    )

    directives.widget(
        funky=FunkyFieldWidget,
    )
    funky = schema.TextLine(
        title="Test funky field",
    )

    directives.read_permission(topsecret="cmf.ModifyPortalContent")
    directives.write_permission(topsecret="cmf.ManagePortal")
    topsecret = schema.TextLine(
        title="Top secret field",
    )


class IMockPortletManager(IPortletManager):
    """Marker interface for the mock portlet manager."""


@implementer(IMockPortletManager)
class MockPortletManager(PortletManager):
    """Mock portlet manager to use in tests."""


@adapter(Interface, IBrowserRequest, IBrowserView, IMockPortletManager)
class MockPortletManagerRenderer(PortletManagerRenderer):
    """Mock portlet manager renderer to use in tests."""

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

        xmlconfig.file(
            "configure.zcml", plone.app.dexterity, context=configurationContext
        )

        if api.env.plone_version() < "5.2":
            # since Plone 5.2 plone.app.widgets is a dummy package only
            import plone.app.widgets

            xmlconfig.file(
                "configure.zcml", plone.app.widgets, context=configurationContext
            )

        import plone.app.standardtiles

        xmlconfig.file(
            "configure.zcml", plone.app.standardtiles, context=configurationContext
        )
        xmlconfig.file(
            "testing.zcml", plone.app.standardtiles, context=configurationContext
        )

        import plone.app.contenttypes

        xmlconfig.file(
            "configure.zcml", plone.app.contenttypes, context=configurationContext
        )

        try:
            import plone.app.drafts

            xmlconfig.file(
                "configure.zcml", plone.app.drafts, context=configurationContext
            )
        except ImportError:
            pass

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, "plone.app.dexterity:default")
        if api.env.plone_version() < "5.2":
            # since Plone 5.2 plone.app.widgets is a dummy package only
            applyProfile(portal, "plone.app.widgets:default")
        applyProfile(portal, "plone.app.standardtiles:default")
        applyProfile(portal, "plone.app.contenttypes:default")

        try:
            # testing support when plone.app.drafts is installed in the env.
            # it needs to also be configured for these tests...
            import plone.app.drafts  # noqa

            applyProfile(portal, "plone.app.drafts:default")
        except ImportError:
            pass

        # ensure plone.app.theming disabled
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        registry = getUtility(IRegistry)
        key = "plone.app.theming.interfaces.IThemeSettings.enabled"
        if key in registry:
            registry[key] = False

        # creates some users
        acl_users = getToolByName(portal, "acl_users")
        acl_users.userFolderAddUser(
            NORMAL_USER_NAME,
            NORMAL_USER_PASSWORD,
            ["Member"],
            [],
        )
        acl_users.userFolderAddUser(
            EDITOR_USER_NAME,
            EDITOR_USER_PASSWORD,
            ["Editor"],
            [],
        )
        acl_users.userFolderAddUser(
            MANAGER_USER_NAME,
            MANAGER_USER_PASSWORD,
            ["Manager"],
            [],
        )

        # register portlet manager and portlet manager renderer
        sm = getSiteManager(portal)
        sm.registerUtility(
            component=MockPortletManager(),
            provided=IMockPortletManager,
            name="mock.portletmanager",
        )
        provideAdapter(MockPortletManagerRenderer)

        from plone.app.standardtiles import embed

        embed.requests.get = RequestsGetMock


class PAStandardtilesTestType(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import plone.app.dexterity

        xmlconfig.file(
            "configure.zcml", plone.app.dexterity, context=configurationContext
        )

        import plone.app.widgets

        xmlconfig.file(
            "configure.zcml", plone.app.widgets, context=configurationContext
        )

        import plone.app.standardtiles

        xmlconfig.file(
            "configure.zcml", plone.app.standardtiles, context=configurationContext
        )
        xmlconfig.file(
            "testing.zcml", plone.app.standardtiles, context=configurationContext
        )

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, "plone.app.dexterity:default")
        applyProfile(portal, "plone.app.standardtiles:default")

        # ensure plone.app.theming disabled
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        registry = getUtility(IRegistry)
        key = "plone.app.theming.interfaces.IThemeSettings.enabled"
        if key in registry:
            registry[key] = False

        # creates some users
        acl_users = getToolByName(portal, "acl_users")
        acl_users.userFolderAddUser(
            NORMAL_USER_NAME,
            NORMAL_USER_PASSWORD,
            ["Member"],
            [],
        )
        acl_users.userFolderAddUser(
            EDITOR_USER_NAME,
            EDITOR_USER_PASSWORD,
            ["Editor"],
            [],
        )
        acl_users.userFolderAddUser(
            MANAGER_USER_NAME,
            MANAGER_USER_PASSWORD,
            ["Manager"],
            [],
        )

        # define the dexterity "junk" type
        fti = DexterityFTI("DecoTestType1")
        fti.schema = "plone.app.standardtiles.testing.ITestType1"
        fti.behaviors = ("plone.app.dexterity.behaviors.metadata.IDublinCore",)
        portal.portal_types._setObject("DecoTestType1", fti)

        # inserts the content of the types defined above
        login(portal, MANAGER_USER_NAME)
        content = portal[portal.invokeFactory("DecoTestType1", "deco-test-type1")]
        content.title = "Test content"
        content.description = "Just a test content"
        content.contributors = ("Jane Doe", "John Doe")
        logout()


PASTANDARDTILES_FIXTURE = PAStandardtiles()
PASTANDARDTILES_TESTTYPE_FIXTURE = PAStandardtilesTestType()

PASTANDARDTILES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PASTANDARDTILES_FIXTURE,), name="PAStandardTiles:Integration"
)
PASTANDARDTILES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PASTANDARDTILES_FIXTURE,), name="PAStandardTiles:Functional"
)
PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PASTANDARDTILES_TESTTYPE_FIXTURE,),
    name="PAStandardTilesTestType:Functional",
)
