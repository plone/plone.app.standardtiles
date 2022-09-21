from lxml import etree
from lxml import html
from plone.app.discussion.browser.comments import CommentForm
from plone.app.layout.globals.interfaces import IViewView
from plone.protect import createToken
from plone.tiles import Tile
from repoze.xmliter.utils import getHTMLSerializer
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


class TileCommentForm(CommentForm):
    prefix = "form"
    action = ""


def protect(raw):
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    parser = getHTMLSerializer([raw], pretty_print=False, encoding="utf-8")
    parser.serializer = html.tostring

    root = parser.tree.getroot()
    token = createToken()

    for form in root.cssselect("form"):
        authenticator = form.cssselect('[name="_authenticator"]')
        if len(authenticator) == 0:
            authenticator = etree.Element("input")
            authenticator.attrib["name"] = "_authenticator"
            authenticator.attrib["type"] = "hidden"
            authenticator.attrib["value"] = token
            form.append(authenticator)
    return parser.serialize().decode("utf-8")


class DiscussionTile(Tile):
    """Discussion tile."""

    def __call__(self):
        alsoProvides(self, IViewView)
        manager = queryMultiAdapter(
            (self.context, self.request, self),
            IViewletManager,
            name="plone.belowcontent",
        )
        viewlet = queryMultiAdapter(
            (self.context, self.request, self, manager), IViewlet, name="plone.comments"
        )
        if viewlet is not None:
            viewlet.form = TileCommentForm
            viewlet.update()

            if isinstance(viewlet.form, TileCommentForm):
                viewlet.form.action = self.url

            # Fix submit redirect from tile to context
            if "location" in self.request.response.headers:
                location = self.request.response.getHeader("location")
                self.request.response.redirect(
                    "".join([self.context.absolute_url(), "#", location.split("#")[-1]])
                )
            return protect("<html><body>%s</body></html>" % viewlet.render())
        return "<html><body></body></html>"
