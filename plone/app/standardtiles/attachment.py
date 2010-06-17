from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IPublishTraverse

from plone.directives import form as directivesform

from plone.tiles import PersistentTile

from plone.namedfile.utils import set_headers, stream_data
from plone.namedfile.field import NamedFile


class IAttachmentTile(directivesform.Schema):

    fileObj = NamedFile(title=u"Please upload a file", required=True)
    linkText = schema.TextLine(title=u"Link text", required=False)


class AttachmentTile(PersistentTile):
    """Attachment tile.
    
    This is a persistent tile which stores a file and optionally link
    text. When rendered, the tile will output an <a /> tag like::
    
        <a href="http://.../@@plone.app.standardtiles.attachment/tile-id/@@download/filename.ext">Link text</a>

    If the link text is not provided, the filename itself will be used.
    
    The tile is a public traversal view, so it will stream the file data
    if the correct filename (matching the uploaded filename), is given in
    the traversal subpath (filename.ext in the example above). Note that the
    ``id`` of the tile is still required for the tile to be able to
    access its persistent data.
    """

    def __call__(self):
        # Not for production use - this should be in a template!
        fileObj = self.data.get('fileObj', None)
        if fileObj is not None:
            filename = fileObj.filename
            linkText = self.data.get('linkText')
            if linkText is None:
                linkText = filename
            fileURL = "%s/@@download/%s" % (self.url, filename,)
            return '<html><body><a href="%s">%s</a></body></html>' % (fileURL, linkText)
        else:
            return '<html><body><em>File not found</em></body></html>'

class AttachmentTileDownload(object):
    """Implementation of the @@download view on the attachment tile.
    
    This is a view onto the AttachmentTile tile view.
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
        
        fileObj = self.context.data.get('fileObj', None)
        if file is None:
            raise NotFound(self, self.filename, self.request)
        
        if not self.filename:
            self.filename = getattr(fileObj, 'filename', '')
        
        set_headers(fileObj, self.request.response, filename=self.filename)
        return stream_data(fileObj)

