from plone.base.interfaces import INonInstallable
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation."""
        return ["plone.app.standardtiles:uninstall"]


def clean_up_registry():
    registry = getUtility(IRegistry)
    records = [
        "plone.app.portlets.PortletManagerBlacklist",
        "plone.app.tiles",
    ]
    for r in records:
        values = list(registry[r])
        for v in values:
            if v.startswith("plone.app.standardtiles"):
                registry[r].remove(v)


def run_after(context):
    clean_up_registry()
