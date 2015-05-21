# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone.app.imaging.interfaces import IImagingSchema
from plone.app.standardtiles import PloneMessageFactory as _
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from plone.supermodel.model import Schema
from plone.tiles import PersistentTile
from zope import schema
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import provider
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

try:
    from plone.protect.interfaces import IDisableCSRFProtection
    HAS_PLONE_PROTECT = True
except ImportError:
    HAS_PLONE_PROTECT = False


@provider(IContextSourceBinder)
def imageScales(context):
    values = []
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

    scale = schema.Choice(
        title=_(u'Select maximum display size'),
        source=imageScales
    )


class ImageTile(PersistentTile):
    """Image tile.

    This is a persistent tile which stores a image and
    selected image scale.
    When rendered, the tile will output an <img /> tag like::

    <img src="http://.../@@plone.app.standardtiles.attachment/tile-id/
    @@images/filename.png" />

    """

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        # Disable CSRF, because imagescales may save a new scale into ZODB
        if HAS_PLONE_PROTECT:
            alsoProvides(self.request, IDisableCSRFProtection)



@implementer(IPublishTraverse)
class ImageDownload(BrowserView):
    def __init__(self, context, request):
        super(ImageDownload, self).__init__(context, request)
        self.stack = []

    def publishTraverse(self, request, name):
        self.stack.append(name)
        return self

    def render(self):
        download = self.context.image.restrictedTraverse("@@download")
        for part in self.stack:
            download = download.publishTraverse(self.request, part)
        # Fix filename with non-ascii characters to be encoded as utf-8
        if download.filename is None:
            file_ = download._getFile()
            filename = getattr(file_, 'filename', download.fieldname)
            if type(filename) == unicode:
                download.filename = filename.encode('utf-8', 'ignore')
        return download()


@implementer(IPublishTraverse)
class ImageScales(BrowserView):
    def __init__(self, context, request):
        super(ImageScales, self).__init__(context, request)
        self.stack = []

    def publishTraverse(self, request, name):
        self.stack.append(name)
        return self

    def render(self):
        """The correct URL to scaled images we want to publish regardless
        of publication state is of the form:
            tile-url/@@images/scaled-imagefile-name
        """
        images = self.context.image.restrictedTraverse("@@images")
        scale = None

        # Traverse the url one part at a time, until we reach the real image
        for part in self.stack:
            scale = images.publishTraverse(self.request, part)
            if scale != images:
                # we're out of the original context (and probably in the
                # imagescale object, which can't be traversed)
                break

        if scale:
            set_headers(scale.data, self.request.response)
            return stream_data(scale.data)
        else:
            return images
