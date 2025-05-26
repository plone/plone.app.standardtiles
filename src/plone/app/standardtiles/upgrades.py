from logging import getLogger
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility


logger = getLogger(__name__)


PROFILE_ID = "profile-plone.app.standardtiles:default"


def upgrade_registry(context, logger=None):
    setup = getToolByName(context, "portal_setup")
    setup.runImportStepFromProfile(PROFILE_ID, "plone.app.registry")


def to_1002(context):
    """Upgrade to version 1002."""
    logger.info("Running upgrade to version 1002")

    registry = getUtility(IRegistry)

    record = registry.get("plone.app.tiles") or []
    if not record:
        logger.info("No plone.app.tiles registry record found, nothing to remove.")
        return

    len_before = len(record)
    record = [value for value in record if "plone.app.standardtiles" not in value]
    registry["plone.app.tiles"] = record
    len_removed = len_before - len(record)

    logger.info("Removed %s deprecated plone.app.tiles registry records.", len_removed)
