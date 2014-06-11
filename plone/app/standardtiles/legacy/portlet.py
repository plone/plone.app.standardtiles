#-*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import implements
from zope.component import getMultiAdapter
from zope import schema

from plone.tiles import Tile
from plone.autoform import directives as form

from plone.app.standardtiles import PloneMessageFactory as _


class IPortletTile(Interface):

    form.omitted('portlet_hash')
    portlet_hash = schema.TextLine(
        title=_(u"The portlet hash"),
        required=False
    )

    portlet_type = schema.Choice(
        title=_(u"The portlet hash"),
        vocabulary=u'standardtiles.available_portlets',
        required=True
    )


class PortletTile(Tile):
    """A tile that renders a portlet."""

    implements(IPortletTile)

    def __call__(self):
        """Return the rendered contents of the portlet specified."""
        # the hash is built into plone.portlets.utils.hashPortletInfo
        # like this:
        # concat_txt = '%(manager)s\n%(category)s\n%(key)s\n%(name)s' % info

        the_hash = self.data.get('portlet_hash')
        renderer = getMultiAdapter((self.context, self.request),
                                   name="render-portlet")
        return u"<html><body>%s</body></html>" % renderer.render_portlet(the_hash)

