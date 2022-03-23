from AccessControl import getSecurityManager
from Acquisition import aq_chain
from Acquisition import aq_inner
from plone.app.layout.navigation.interfaces import INavigationRoot
from z3c.form.interfaces import IFieldWidget
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.security.interfaces import IPermission


def getNavigationRoot(context):
    for obj in aq_chain(aq_inner(context)):
        if INavigationRoot.providedBy(obj):
            break
    return obj


class PermissionChecker:
    def __init__(self, permissions, context):
        self.permissions = permissions
        self.context = context
        self.sm = getSecurityManager()
        self.cache = {}

    def allowed(self, field_name):
        permission_name = self.permissions.get(field_name, None)
        if permission_name is not None:
            if permission_name not in self.cache:
                permission = queryUtility(IPermission, name=permission_name)
                if permission is None:
                    self.cache[permission_name] = True
                else:
                    self.cache[permission_name] = bool(
                        self.sm.checkPermission(permission.title, self.context),
                    )
        return self.cache.get(permission_name, True)


def _getWidgetName(field, widgets, request):
    if field.__name__ in widgets:
        factory = widgets[field.__name__]
    else:
        factory = getMultiAdapter((field, request), IFieldWidget)
    if isinstance(factory, str):
        return factory
    if not isinstance(factory, type):
        factory = factory.__class__
    return f"{factory.__module__}.{factory.__name__}"


def isVisible(name, omitted):
    value = omitted.get(name, False)
    if isinstance(value, str):
        return value == "false"
    return not bool(value)
