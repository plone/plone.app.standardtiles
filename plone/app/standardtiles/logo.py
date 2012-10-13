from zope.schema import TextLine
from zope.component import getMultiAdapter

from plone.supermodel import model
from plone.autoform import directives as form
from plone.namedfile.field import NamedImage
from plone.tiles import PersistentTile
from plone.app.tiles import MessageFactory as _


class ILogoTile(model.Schema):
    """
    """

    form.widget(picture='plone.app.imagetile.imagewidget.ImageFieldWidget')
    picture = NamedImage(
        title=_('Select an image'),
        required=True,
        )

    title = TextLine(
        title=_('Image title.'),
        required=False,
        )


class LogoTile(PersistentTile):
    """
    """

    def __init__(self, *arg, **kw):
        super(LogoTile, self).__init__(*arg, **kw)
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')

    @property
    def portal(self):
        return self.portal_state.portal()

    @property
    def logoName(self):
        bprops = self.portal.restrictedTraverse('base_properties', None)
        if bprops is not None:
            return bprops.logoName
        else:
            return 'logo.jpg'

    @property
    def logoTitle(self):
        return self.portal_state.portal_title()

    @property
    def logo_tag(self):
        return self.portal.restrictedTraverse(self.logoName).tag(
            title=self.logoTitle, alt=self.logoTitle)

    @property
    def navigation_root_title(self):
        return self.portal_state.navigation_root_title()

    @property
    def navigation_root_url(self):
        return self.portal_state.navigation_root_url()

    @property
    def actions(self):
        return [{
                'name': 'edit',
                'url': '@@edit-tile',
                'title': _('Edit'),
            }, {
                'name': 'remove',
                'url': '@@delete-tile',
                'title': _('Remove'),
            }]
