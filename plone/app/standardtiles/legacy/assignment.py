# -*- coding: utf-8 -*-
from BTrees.OOBTree import OOBTree
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.standardtiles.interfaces import IPortletManager
from plone.app.standardtiles.interfaces import IPortletManagerAssignment
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignable
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import implementer

# The '+' view of the portlet manager
# is applied on the assignment not on the manager itself.
# We need a custom marker interface for the assignment
# of our portlet manager... here is it!

@implementer(IPortletManagerAssignment)
class Mapping(PortletAssignmentMapping):
    pass


@adapter(ILocalPortletAssignable, IPortletManager)
@implementer(IPortletAssignmentMapping)
def localPortletAssignmentMappingAdapter(context, manager):
    """This is pretty much the same code of the original one from

    `plone.app.portlets.assignable.localPortletAssignmentMappingAdapter`

    but it changes the assignment klass with `Mapping`.

    This is needed in order to use our custom view '+'
    for adding the portlet.
    """
    annotations = IAnnotations(context)
    local = annotations.get(CONTEXT_ASSIGNMENT_KEY, None)
    if local is None:
        local = annotations[CONTEXT_ASSIGNMENT_KEY] = OOBTree()

    portlets = local.get(manager.__name__, None)
    if portlets is None:
        portlets = local[manager.__name__] = Mapping(manager=manager.__name__,
                                                     category=CONTEXT_CATEGORY)

    # XXX: For graceful migration
    if not getattr(portlets, '__manager__', ''):
        portlets.__manager__ = manager.__name__

    if not getattr(portlets, '__category__', ''):
        portlets.__category__ = CONTEXT_CATEGORY

    return portlets
