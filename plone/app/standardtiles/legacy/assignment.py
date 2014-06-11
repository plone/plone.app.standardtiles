from zope.interface import implementer
from zope.interface import Interface
from zope.component import adapter
from zope.annotation.interfaces import IAnnotations

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignable

from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.constants import CONTEXT_CATEGORY

from BTrees.OOBTree import OOBTree

from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.standardtiles.interfaces import IPortletManager


class IOurAssignment(Interface):
    pass


@implementer(IOurAssignment)
class OurMapping(PortletAssignmentMapping):
    pass


@adapter(ILocalPortletAssignable, IPortletManager)
@implementer(IPortletAssignmentMapping)
def localPortletAssignmentMappingAdapter(context, manager):
    """Zope 2 version of the localPortletAssignmentMappingAdapter factory.
    """
    annotations = IAnnotations(context)
    local = annotations.get(CONTEXT_ASSIGNMENT_KEY, None)
    if local is None:
        local = annotations[CONTEXT_ASSIGNMENT_KEY] = OOBTree()

    portlets = local.get(manager.__name__, None)
    if portlets is None:
        portlets = local[manager.__name__] = OurMapping(manager=manager.__name__,
                                                        category=CONTEXT_CATEGORY)

    # XXX: For graceful migration
    if not getattr(portlets, '__manager__', ''):
        portlets.__manager__ = manager.__name__

    if not getattr(portlets, '__category__', ''):
        portlets.__category__ = CONTEXT_CATEGORY

    return portlets
