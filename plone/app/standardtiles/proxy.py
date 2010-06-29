from zope import schema
from plone.tiles import Tile
from plone.directives import form as directivesform
from Products.Five.browser import BrowserView
from lxml import etree, cssselect


class IProxyTile(directivesform.Schema):
    contentPath = schema.TextLine(title=u"Path to the content object to show, starting from the site root.",
                                  required=True)


class ProxyTile(Tile):
    """Proxy tile.

    It renders the @@proxy-view browser view on the specified content
    object.
    """

    def __call__(self):
        portal = self.context.restrictedTraverse('@@plone_portal_state').portal()
        content = portal.restrictedTraverse([self.data.get('contentPath')])
        view = content.restrictedTraverse('@@proxy-view')
        return view()


class ProxyView(BrowserView):
    def __call__(self):
        layout = self.context.getLayout()
        out = self.context.restrictedTraverse([layout])()
        htmlparser = etree.HTMLParser()
        tree = etree.fromstring(out, htmlparser)
        sel = cssselect.CSSSelector('#content')
        content = sel(tree)[0]
        return etree.tostring(content)
