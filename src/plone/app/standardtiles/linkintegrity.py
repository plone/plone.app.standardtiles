from plone.app.linkintegrity.interfaces import IRetriever
from plone.app.linkintegrity.parser import extractLinks
from plone.app.standardtiles import existingcontent
from plone.app.standardtiles import html
from zope.component import adapter
from zope.interface import implementer


@implementer(IRetriever)
@adapter(html.HTMLTile)
class HTMLTile(object):
    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        content = self.context.data["content"]
        # layout behavior tile storage hard codes 'utf-8' encoding
        # thus we do the same.
        links = set(extractLinks(content, "utf-8"))
        return links


@implementer(IRetriever)
@adapter(existingcontent.ExistingContentTile)
class ExistingContentTile(object):
    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        content_uid = self.context.data["content_uid"]
        links = set(["../resolveuid/%s" % content_uid])
        return links
