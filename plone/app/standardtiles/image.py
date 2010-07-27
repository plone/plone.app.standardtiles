from zope.interface import directlyProvides, implements, implementsOnly, implementer, Interface
from zope import schema
from zope.component import adapter, getUtility
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory, IChoice
from zope.app.component.hooks import getSite
from z3c.form.i18n import MessageFactory as _
from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationChoice
from z3c.relationfield.interfaces import IHasOutgoingRelations

from plone.directives import form as directivesform
from plone.registry.interfaces import IRegistry

from plone.tiles import PersistentTile

from z3c.form.browser.select import SelectWidget
from z3c.form.interfaces import IFormLayer, IFieldWidget, ISelectWidget, ISubForm
from z3c.form.widget import FieldWidget
from z3c.form import field
from z3c.form import form

from Products.CMFCore.utils import getToolByName

from zope.container.interfaces import INameChooser


class IImagePreviewSelectWidget(ISelectWidget):
    """Marker interface for the image preview select widget."""
    pass


class ImagePreviewSelectWidget(SelectWidget):
    """A select widget for images that shows a preview of the selected
    image next to it.
    """

    implementsOnly(IImagePreviewSelectWidget)
    
    klass = u'image-preview-select-widget'
    prompt = True

    promptMessage = _('select an image ...')

    def update(self):
        self.upload = ImageUploadForm(None, self.request)
        self.upload.update()

        if not self.ignoreRequest:
            data, errors = self.upload.extractData()
            if errors:
                return
            
            filedata = data['image_upload']
            image_upload_widget = self.upload.widgets['image_upload']
            
            if filedata:
                site = getSite()
                registry = getUtility(IRegistry)
                images_path = str(registry['plone.app.standardtiles.interfaces.IStandardTilesSettings.images_repo_path']) # XXX: why doesn't it return a string instead of unicode?
                repo = site.unrestrictedTraverse(images_path)
                filename = image_upload_widget.filename
                
                temp_id = repo.generateUniqueId(filename)
                repo.invokeFactory('Image', temp_id)
                image = getattr(repo, temp_id)
                image.setImage(filedata)

                # set a unique name for the uploaded image
                namechooser = INameChooser(repo)
                unique_id = namechooser.chooseName(filename, image)
                image.setId(unique_id)
                
                intids = getUtility(IIntIds)
                image_id = intids.getId(image)

                self.request.form[self.name] = str(image_id)

        super(ImagePreviewSelectWidget, self).update()

    def js(self):
        return  """\
        (function($) {
          $().ready(function() {

            var image_preview = $('#%(id)s-image-preview');
            if (image_preview.attr('src')) {
              image_preview.prepOverlay({
                subtype: 'image',
                urlmatch: '/image_thumb$',
                urlreplace: '/image_preview'
              });
            }

            $('#%(id)s').change(function() {
              var selected = $('#%(id)s option:selected');
              var url = selected.attr('title');
              $('#%(id)s-image-preview').attr('src', url);

              var overlay = image_preview.attr("rel");
              $(overlay).remove();
              image_preview.removeAttr("rel");
              image_preview.prepOverlay({
                subtype: 'image',
                urlmatch: '/image_thumb$',
                urlreplace: '/image_preview'
              });
            });

          })
        })(jQuery); 
        """ % {'id': self.id}

    def getImageURLFromId(self, imageId):
        """Look-up the URL for the src attribute of an image tag from
        its id."""
        
        if imageId == self.noValueToken:
            return ''
        try:
            imageId = int(imageId)
        except ValueError:
            raise Exception('The image id must be an integer')
        intids = getUtility(IIntIds)
        image = intids.queryObject(imageId)
        if image:
            return image.absolute_url()
        return ''  # image not found
        # XXX: should point to a "image-not-found" image


@adapter(IChoice,
         Interface,
         IFormLayer)
@implementer(IFieldWidget)
def ImagePreviewSelectFieldWidget(field, source, request=None):
    """IFieldWidget factory for ImagePreviewSelectWidget."""
    # BBB: emulate our pre-2.0 signature (field, request)
    if request is None:
        real_request = source
    else:
        real_request = request
    fieldwidget = FieldWidget(field, ImagePreviewSelectWidget(real_request))
    return fieldwidget


class ImageUploadForm(form.Form):
    implements(ISubForm)
    css_class = 'image_subform'

    fields = field.Fields(
        schema.Bytes(__name__='image_upload', required=False)
        )


def availableImagesVocabulary(context):
    """Vocabulary composed of Images inside the '/images' folder
    at the site root.
    """
    site = getSite()
    catalog = getToolByName(site, 'portal_catalog')
    portal_state = site.restrictedTraverse('@@plone_portal_state')
    root_path = portal_state.navigation_root_path()
    registry = getUtility(IRegistry)
    images_path = "%s/%s" % (root_path, registry['plone.app.standardtiles.interfaces.IStandardTilesSettings.images_repo_path'])
    results = catalog(path=images_path,
                      portal_type='Image')
    intids = getUtility(IIntIds)
    terms = [SimpleTerm(value=intids.getId(r.getObject()), title=r.id) for r in results]
    return SimpleVocabulary(terms)
directlyProvides(availableImagesVocabulary, IVocabularyFactory)


class IImageTile(directivesform.Schema):

    directivesform.widget(imageId=ImagePreviewSelectFieldWidget)
    imageId = RelationChoice(title=u"Image Id", required=True,
                             vocabulary=u"Available Images")
    imageId._type = int
    altText = schema.TextLine(title=u"Alternative text", required=False,
                              missing_value=u'')


class ImageTile(PersistentTile):
    """Image tile.
    
    This is a transient tile which stores a reference to an image and
    optionally alt text. When rendered, the tile will look-up the image
    url and output an <img /> tag.
    """

    implements(IHasOutgoingRelations)
    
    def __call__(self):
        # Not for production use - this should be in a template!
        imageId = self.data.get('imageId')
        imageId = int(imageId)
        intids = getUtility(IIntIds)
        image = intids.queryObject(imageId)
        if image is not None:
            imageURL = image.absolute_url()
            altText = self.data.get('altText')
            if altText is not None:
                altText = altText.replace('"', '\"')
            else:
                altText = ''
            return '<html><body><img src="%s" alt="%s" /></body></html>' % (imageURL, altText)
        else:
            return '<html><body><em>Image not found.</em></body></html>'
