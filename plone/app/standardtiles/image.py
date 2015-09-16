# -*- coding: utf-8 -*-
from plone.app.standardtiles import _PMF as _
from plone.autoform.directives import widget
from plone.namedfile.field import NamedBlobFile
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from plone.tiles import PersistentTile
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

try:
    from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
    HAS_PLONE_5 = True
except ImportError:
    from plone.app.imaging.interfaces import IImagingSchema
    HAS_PLONE_5 = False

try:
    from plone.protect.interfaces import IDisableCSRFProtection
    HAS_PLONE_PROTECT = True
except ImportError:
    HAS_PLONE_PROTECT = False


def get_settings():
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IImagingSchema,
                                     prefix="plone",
                                     check=False)
    return settings


@provider(IContextSourceBinder)
def image_scales(context):
    values = []
    if HAS_PLONE_5:
        settings = get_settings()
    else:
        settings = IImagingSchema(getSite())
    for allowed_size in settings.allowed_sizes:
        name = allowed_size.split()[0]
        if name not in ("thumb", "tile", "icon", "listing"):
            values.append(SimpleTerm(name, name, _(allowed_size)))
    return SimpleVocabulary(values)


class IImageTile(Schema):

    image = NamedBlobFile(
        title=_(u'Please, upload an image'),
    )

    title = schema.TextLine(
        title=_(u'Set optional title'),
        required=False
    )

    widget(scale=RadioFieldWidget)
    scale = schema.Choice(
        title=_(u'Select maximum display size'),
        source=image_scales
    )


class ImageTile(PersistentTile):
    """Image tile.

    This is a persistent tile which stores an image with
    selected image scale.

    When rendered, the tile will output an <img /> tag like::

    <img src=".../@@plone.app.standardtiles.image/tile-id/
              @@images/bcc7be5d-75cc-4cfd-9d3a-4ad231aa01de.png" />

    """
