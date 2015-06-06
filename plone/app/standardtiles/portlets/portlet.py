#-*- coding: utf-8 -*-
from plone.app.portlets.interfaces import IDeferredPortletRenderer
from plone.app.portlets.utils import assignment_from_key
from plone.app.standardtiles import PloneMessageFactory as _
from plone.autoform import directives as form
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.utils import unhashPortletInfo
from plone.tiles import Tile
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implements


class IPortletTile(Interface):

    form.omitted('portlet_hash')
    portlet_hash = schema.TextLine(
        title=_(u"Portlet hash"),
        required=False
    )

    portlet_type = schema.Choice(
        title=_(u"Portlet type"),
        vocabulary=u'standardtiles.available_portlets',
        required=True
    )


class PortletTile(Tile):
    """A tile that renders a portlet."""

    implements(IPortletTile)

    def __call__(self):
        """Return the rendered contents of the portlet specified."""
        # portletHash is built into plone.portlets.utils.hashPortletInfo
        # like this:
        # concat_txt = '%(manager)s\n%(category)s\n%(key)s\n%(name)s' % info

        portlethash = self.data.get('portlet_hash')

        # Prepare the portlet and render the data
        info = unhashPortletInfo(portlethash)
        manager = getUtility(IPortletManager, info['manager'])

        assignment = assignment_from_key(context=self.context,
                                         manager_name=info['manager'],
                                         category=info['category'],
                                         key=info['key'],
                                         name=info['name'])
        renderer = getMultiAdapter(
            (self.context, self.request, self, manager, assignment.data),
            IPortletRenderer)
        renderer = renderer.__of__(self.context)

        # This is required by some portlets and not set by
        # the 'portlet-renderer' helper view:
        renderer.__portlet_metadata__ = info

        renderer.update()
        if IDeferredPortletRenderer.providedBy(renderer):
            # if this is a deferred load, prepare now the data
            renderer.deferred_update()

        return u"<html><body>%s</body></html>" % renderer.render()
