from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IPublishTraverse

from plone.directives import form as directivesform
from Products.CMFCore.utils import getToolByName

from plone.tiles import PersistentTile

from plone.namedfile.utils import set_headers, stream_data
from plone.namedfile.field import NamedFile
from plone.namedfile.interfaces import INamed

class IAttachmentTile(directivesform.Schema):

    files = schema.List(
        title=u'Upload files',
        value_type=NamedFile(title=u"Please upload a file", required=True))


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
        self.update()
        return self.index()

    def update(self):
        pass

    def file_size(self, file_):
        """Returns the file-size of the `file_` in KB.
        """
        if INamed.providedBy(file_):
            return file_.getSize() / 1024
        else:
            return 0

    def get_icon_for(self, file_):
        """Returns the best icon for the `file_`
        """
        mtr = getToolByName(self.context, 'mimetypes_registry', None)
        if mtr is None:
            return self.context.getIcon()
        lookup = mtr.lookup(file_.contentType)
        if lookup:
            mti = lookup[0]
            try:
                self.context.restrictedTraverse(mti.icon_path)
                return mti.icon_path
            except (NotFound, KeyError, AttributeError):
                pass
        return self.context.getIcon()


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
        
        for file_ in self.context.data.get('files', ()):
            if self.filename == getattr(file_, 'filename', ''):
                set_headers(file_, self.request.response,
                            filename=self.filename)
                return stream_data(file_)

        raise NotFound(self, self.filename, self.request)
