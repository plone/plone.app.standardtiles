import collections
from zope.component import queryMultiAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.tiles import Tile
from plone.app.standardtiles.utils import getNavigationRoot
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.utils import typesToList
from Products.CMFCore.utils import getToolByName


class INavtreeFactory(Interface):
    """Marker interface for catalog builder functions."""

    def __call__(context, request):
        """Return a CatalogNavTree instance."""


class CatalogNavTree(object):
    def __init__(self, context, request):
        self.build(context, request)

    def build(self, context, request):
        context = aq_inner(context)

        # If we are at a default page use the folder as context for the navtree
        container = aq_parent(context)
        isp = queryMultiAdapter((container, request), name="default_page", default=None)
        if isp is not None and isp.isDefaultPage(context):
            context = container

        contextPath = "/".join(context.getPhysicalPath())
        contextPathLen = len(contextPath)
        contextParentPath = contextPath.rsplit("/", 1)[0]
        navrootPath = "/".join(getNavigationRoot(context).getPhysicalPath())

        query = {}
        query["path"] = dict(query=contextPath,
                             navtree=True,
                             navtree_start=navrootPath.count("/"))
        query["portal_type"] = typesToList(context)
        query["sort_on"] = "getObjPositionInParent"
        query["sort_order"] = "asc"

        catalog = getToolByName(context, "portal_catalog")
        results = catalog.searchResults(query)
        cache = {}
        cache[navrootPath] = {"current": False, "currentParent": True, "children": []}
        for brain in results:
            path = brain.getPath()
            pathLen = len(path)
            parentPath = path.rsplit("/", 1)[0]
            isAncestor = isCurrent = isCurrentParent = False

            if path == contextPath:
                isCurrent = True
            elif contextPathLen > pathLen:
                isAncestor = contextPath.startswith(path + "/")
                isCurrentParent = path == contextParentPath

            if brain.exclude_from_nav and not isCurrentParent:
                continue

            node = {"brain": brain,
                    "path" : path,
                    "current" : isCurrent,
                    "currentParent" : isCurrentParent,
                    "ancestor": isAncestor }

            oldNode = cache.get(path, None)
            if oldNode is not None:
                oldNode.update(node)
                node = oldNode
            else:
                node["children"] = []
                cache[path] = node

            parentNode = cache.get(parentPath, None)
            if parentNode is None:
                parentNode = cache[parentPath] = dict(children=[node])
            else:
                parentNode["children"].append(node)
            node["parent"] = parentNode

        self.tree = cache
        self.root = cache[navrootPath]


    def __iter__(self):
        """Breadth-first iterator for navtree nodes which allows
        modifications of the tree during iteration. Modifications
        are given by passing a command to the next() method of the
        generator. For example:

        >>> tree = CatalogNavTree(context, request)
        >>> g = tree.iter()
        >>> value = g.next()
        >>> try:
        ...     while True:
        ...        if value.portal_type == "Collection":
        ...            value = g.send("prune")
        ...        else:
        ...            value = g.next()
        ... except StopIteration:
        ...     pass

        The supported commands are:

        * purge: remove the node and all its children from the tree
        * prune: remove all children of this node from the tree

        In addition you may also modify the datastructures directly
        during iteration.
        """
        queue = collections.deque([self.root])
        while queue:
            node = queue.popleft()
            action = (yield node)
            if action == "purge":
                node["parent"]["children"].remove(node)
                continue
            elif action == "prune":
                node["children"] = []
                continue

            for child in node.get("children", []):
                queue.append(child)

    iter = __iter__



class TreeFactory(object):
    implements(INavtreeFactory)
    adapts(Interface, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return CatalogNavTree(self.context, self.request)


class NavigationTile(Tile):

    def update(self):
        portal_types = getToolByName(self.context, "portal_types")
        type_titles = dict([(fti.getId(), fti.Title()) for fti in portal_types.listTypeInfo()])

        portal_properties = getToolByName(self.context, "portal_properties")
        use_view_types = portal_properties.site_properties.typesUseViewActionInListings
        normalize = getUtility(IIDNormalizer).normalize
        treefactory = getMultiAdapter((self.context, self.request), INavtreeFactory)
        tree = treefactory()

        for node in tree.iter():
            brain = node.get("brain", None)
            if brain is None:
                continue
            node["title"] = brain.Title
            node["description"] = brain.Description or None
            node["portal_type"] = normalize(brain.portal_type)
            node["portal_type_title"] = type_titles.get(brain.portal_type, brain.portal_type)
            node["url"] = "%s/view" % brain.getURL() if brain.portal_type in use_view_types else brain.getURL()
            node["review_state"] = normalize(brain.review_state)
            node["folderish"] = brain.is_folderish
            node["class"] = " ".join(filter(None,
                                            ["active" if node["current"] or node["currentParent"] else None,
                                             "current" if node["current"] else None])) or None
            
        if "brain" in tree.root:
            self.tree = [tree.root]
        else:
            self.tree = tree.root["children"]

    def __call__(self):
        self.update()
        return self.index()

