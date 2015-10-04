# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interface import IBrowserDefault
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.navigation.defaultpage import isDefaultPage
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.vocabularies.catalog import CatalogSource as CatalogSourceBase
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.supermodel.model import Schema
from plone.tiles import Tile
from plone.uuid.interfaces import IUUID
from z3c.form.interfaces import IValue
from z3c.form.util import getSpecification
from zope import schema
from zope.component import adapter
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implements


def uuidToFolderishPath(context, uuid):
    """Return closest relative folderish path for the given UUID
    or an empty string for the site root
    """
    if uuid:
        catalog = getToolByName(context, 'portal_catalog')
        res = catalog and catalog.unrestrictedSearchResults(UID=uuid)
        if res and len(res) == 1:
            ob = res[0]._unrestrictedGetObject()
            # If not folderish, use its parent instead
            if not IFolderish.providedBy(ob):
                ob = aq_parent(ob)
            return '/'.join(ob.getPhysicalPath()[2:])
    return ''


class CatalogSource(CatalogSourceBase):
    """Navigation tile specific catalog source to allow targeted widget"""


class INavigationTile(Schema):
    """A tile which can render the navigation tree."""

    name = schema.TextLine(
            title=_(u"Title"),
            description=_(u"The title of the navigation tree."),
            default=u"",
            required=False,)

    root = schema.Choice(
            title=_(u"Root node"),
            description=_(u"You may search for and choose a folder to act as "
                           "the root of the navigation tree.  Leave blank to "
                           "use the Plone site root."),
            source=CatalogSource(),
            required=False)

    includeTop = schema.Bool(
            title=_(u"Include top node"),
            description=_(u"Whether or not to show the top, or 'root', node "
                           "in the navigation tree. This is affected by the "
                           "'Start level' setting."),
            default=False,
            required=False)

    currentFolderOnly = schema.Bool(
            title=_(u"Only show the contents of the current folder."),
            description=_(u"If selected, the navigation tree will only show "
                           "the current folder and its children at all "
                           "times."),
            default=False,
            required=False)

    topLevel = schema.Int(
            title=_(u"Start level"),
            description=_(u"An integer value that specifies the number of "
                           "folder levels below the site root that must be "
                           "exceeded before the navigation tree will display. "
                           "0 means that the navigation tree should be "
                           "displayed everywhere including pages in the root "
                           "of the site. 1 means the tree only shows up "
                           "inside folders located in the root and downwards, "
                           "never showing at the top level."),
            default=0,
            required=False)

    bottomLevel = schema.Int(
            title=_(u"Navigation tree depth"),
            description=_(u"How many folders should be included before the "
                           "navigation tree stops. 0 means no limit. 1 only "
                           "includes the root folder."),
            default=0,
            required=False)


@implementer(IValue)
@adapter(None, None, None, getSpecification(INavigationTile['root']), None)
class DefaultRoot(object):
    def __init__(self, context, request, form, field, widget):
        self.context = context

    def get(self):
        # Return UUID for the closest container or None for the site root
        if not IFolderish.providedBy(self.context):
            return IUUID(aq_parent(self.context), None)
        else:
            return IUUID(self.context, None)


class NavigationTile(Tile):

    implements(INavigationTile)

    def __init__(self, *arg, **kw):
        super(NavigationTile, self).__init__(*arg, **kw)
        self.urltool = getToolByName(self.context, 'portal_url')

    def title(self):
        return self.data.get('name', u'')

    @property
    def available(self):
        rootpath = self.getNavRootPath()
        if rootpath is None:
            return False

        tree = self.getNavTree()
        return len(tree['children']) > 0

    def include_top(self):
        return self.data.get('includeTop', False)

    def navigation_root(self):
        return self.getNavRoot()

    def root_type_name(self):
        root = self.getNavRoot()
        return queryUtility(IIDNormalizer).normalize(root.portal_type)

    def root_item_class(self):
        context = aq_inner(self.context)
        root = self.getNavRoot()
        container = aq_parent(context)
        if (aq_base(root) is aq_base(context) or
                (aq_base(root) is aq_base(container) and
                isDefaultPage(container, context))):
            return 'navTreeCurrentItem'
        return ''

    def root_icon(self):
        ploneview = getMultiAdapter((self.context, self.request),
                                    name=u'plone')
        icon = ploneview.getIcon(self.getNavRoot())
        return icon.url

    def root_is_portal(self):
        root = self.getNavRoot()
        return aq_base(root) is aq_base(self.urltool.getPortalObject())

    def createNavTree(self):
        data = self.getNavTree()
        bottomLevel = self.data.get('bottomLevel') or 0
        return self.recurse(children=data.get('children', []),
                            level=1, bottomLevel=bottomLevel)

    recurse = ViewPageTemplateFile('templates/navigation_recurse.pt')

    # Cached lookups

    @memoize
    def getNavRootPath(self):
        currentFolderOnly = self.data.get('currentFolderOnly') or False
        topLevel = self.data.get('topLevel') or 0
        tileRoot = uuidToFolderishPath(self.context, self.data.get('root'))
        return getRootPath(self.context, currentFolderOnly, topLevel, tileRoot)

    @memoize
    def getNavRoot(self, _marker=[]):
        portal = self.urltool.getPortalObject()
        rootPath = self.getNavRootPath()
        if rootPath is None:
            return portal

        if rootPath == self.urltool.getPortalPath():
            return portal
        else:
            try:
                return portal.unrestrictedTraverse(rootPath)
            except (AttributeError, KeyError,):
                return portal

    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)
        queryBuilder = getMultiAdapter((context, self),
                                       INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context,
                               query=queryBuilder(), strategy=strategy)


class QueryBuilder(NavtreeQueryBuilder):
    """Build a navtree query based on the settings in navtree_properties
    and those set on the tile.
    """
    implements(INavigationQueryBuilder)
    adapts(Interface, INavigationTile)

    def __init__(self, context, tile):
        super(QueryBuilder, self).__init__(context)

        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        tileRoot = uuidToFolderishPath(context, tile.data.get('root'))
        rootPath = getNavigationRoot(context, relativeRoot=tileRoot)
        currentPath = '/'.join(context.getPhysicalPath())

        # override query path with tile path if needed
        if currentPath != rootPath and \
           not currentPath.startswith(rootPath + '/'):
            self.query['path'] = {'query': rootPath, 'depth': 1}
        else:
            self.query['path'] = {'query': currentPath, 'navtree': 1}

        topLevel = tile.data.get('topLevel') or navtree_properties.getProperty('topLevel', 0)
        if topLevel and topLevel > 0:
            self.query['path']['navtree_start'] = topLevel + 1


class NavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the default navigation tile."""
    implements(INavtreeStrategy)
    adapts(Interface, INavigationTile)

    def __init__(self, context, tile):
        SitemapNavtreeStrategy.__init__(self, context, tile)
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        # XXX: We can't do this with a 'depth' query to EPI...
        self.bottomLevel = tile.data.get('bottomLevel') or \
                           navtree_properties.getProperty('bottomLevel', 0)

        currentFolderOnly = tile.data.get('currentFolderOnly') or \
                            navtree_properties.getProperty(
                                    'currentFolderOnlyInNavtree', False)
        topLevel = tile.data.get('topLevel') or \
                   navtree_properties.getProperty('topLevel', 0)
        tileRoot = uuidToFolderishPath(context, tile.data.get('root'))
        self.rootPath = getRootPath(context, currentFolderOnly,
                                    topLevel, tileRoot)

    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)
        if sitemapDecision == False:
            return False
        depth = node.get('depth', 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        else:
            return True


def getRootPath(context, currentFolderOnly, topLevel, root):
    """Helper function to calculate the real root path."""
    context = aq_inner(context)
    if currentFolderOnly:
        folderish = getattr(aq_base(context),
                            'isPrincipiaFolderish', False) and \
                    not INonStructuralFolder.providedBy(context)
        parent = aq_parent(context)

        is_default_page = False
        browser_default = IBrowserDefault(parent, None)
        if browser_default is not None:
            browser_default_page = browser_default.getDefaultPage()
            is_default_page = (browser_default_page == context.getId())

        if not folderish or is_default_page:
            return '/'.join(parent.getPhysicalPath())
        else:
            return '/'.join(context.getPhysicalPath())

    rootPath = getNavigationRoot(context, relativeRoot=root)

    # Adjust for topLevel
    if topLevel > 0:
        contextPath = '/'.join(context.getPhysicalPath())
        if not contextPath.startswith(rootPath):
            return None
        contextSubPathElements = contextPath[len(rootPath) + 1:]
        if contextSubPathElements:
            contextSubPathElements = contextSubPathElements.split('/')
            if len(contextSubPathElements) < topLevel:
                return None
            rootPath = '%s/%s' % (rootPath,
                            '/'.join(contextSubPathElements[:topLevel]))
        else:
            return None

    return rootPath
