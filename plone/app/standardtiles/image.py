from zope import schema
from zope.schema import getFields
from zope.interface import implements, Interface
from zope.component import adapts
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IPublishTraverse

from plone.directives import form as directivesform

from plone.tiles import PersistentTile
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.data import PersistentTileDataManager

from plone.namedfile.utils import set_headers, stream_data
from plone.namedfile.field import NamedImage as NamedImageField
from plone.namedfile import NamedImage

from persistent.dict import PersistentDict


class IImageTileType(Interface):
    pass


class IImageTile(directivesform.Schema):

    image = NamedImageField(title=u"Please upload an image", required=True)
    altText = schema.TextLine(title=u"Alternative text", required=False)


class ImageTileDataManager(PersistentTileDataManager):
    """A data manager for the image tile. It stores the image in the '/images'
    folder of the portal, and the altText in the attributes.
    """

    implements(ITileDataManager)
    adapts(IImageTileType)

    def get(self):
        data = dict(self.annotations.get(self.key, {}))
        if self.tileType is not None and self.tileType.schema is not None:
            for name, field in getFields(self.tileType.schema).items():
                if name not in data:
                    data[name] = field.missing_value
        filename = data['image_name']
        atimage = getattr(self.context.images, filename, None)
        if atimage is not None:
            data['image'] = NamedImage(atimage.getImage().data, filename=filename)
        return data

    def set(self, data):
        image = data['image']
        repo = self.context.images
        repo.invokeFactory('Image', image.filename)
        atimage = getattr(repo, image.filename)
        atimage.setImage(image.data)
        data['image_name'] = image.filename
        self.annotations[self.key] = PersistentDict(data)


class ImageTile(PersistentTile):
    """Example image tile.
    
    This is a persistent tile which stores an image and optionally alt
    text. When rendered, the tile will output an <img /> tag like::
    
        <img src="http://.../@@plone.app.standardtiles.image/tile-id/@@download/filename.gif" />
    
    The tile is a publish traversal view, so it will stream the file data
    if the correct filename (matching the uploaded filename), is given in
    the traversal subpath (filename.gif in the example above). Note that the
    ``id`` query string parameter is still required for the tile to be able to
    access its persistent data.
    """

    implements(IImageTileType)

    def __call__(self):
        # Not for production use - this should be in a template!
        image = self.data.get('image', None)
        if image is not None:
            altText = self.data.get('altText', '').replace('"', '\"')
            filename = image.filename
            imageURL = "%s/@@download/%s" % (self.url, filename,)
            return '<html><body><img src="%s" alt="%s" /></body></html>' % (imageURL, altText)
        else:
            return '<html><body><em>No image set</em></body></html>'

class ImageTileDownload(object):
    """Implementation of the @@download view on the image tile.
    
    This is a view onto the ImageTile tile view.
    """
    
    implements(IPublishTraverse)
    filename = None
    
    def publishTraverse(self, request, name):
        if self.filename is None:
            self.filename = name
            return self
        raise NotFound(name)
    
    def __call__(self):
        """Render the file to the browser
        """
        
        image = self.context.data.get('image', None)
        if image is None:
            raise NotFound(self, self.filename, self.request)
        
        if not self.filename:
            self.filename = getattr(image, 'filename', '')
        
        set_headers(image, self.request.response, filename=self.filename)
        return stream_data(image)

