Layout tiles
============

Here we show up the main tiles used for the page layout.

First, we set up a browser instance and get Manager privileges::

    >>> from plone.testing.z2 import Browser
    >>> app = layer['app']
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> portal = layer['portal']
    >>> portalURL = portal.absolute_url()

    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
    >>> setRoles(portal, TEST_USER_ID, ['Manager'])

    >>> import transaction
    >>> transaction.commit() # make the browser see this role

We also keep another testbrowser handy for testing how tiles are rendered if
you're not logged in::

    >>> unprivileged_browser = Browser(app)

We create a page in the site to use it in tests later::

    >>> browser.open(portalURL + '/createObject?type_name=Document')
    >>> browser.getControl(name='title').value = 'A simple page'
    >>> browser.getControl(name='description').value = 'A description'
    >>> browser.getControl('Save').click()
    >>> pageURL = browser.url
    >>> pageURL
    'http://nohost/plone/a-simple-page'

Basic layout
------------

Tiles like the colophon don't need any config parameters::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.colophon')
    >>> unprivileged_browser.contents
    '...This site was built using the Plone Open Source CMS/WCM...'

Head title tile on the portal object::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.headtitle')
    >>> unprivileged_browser.contents
    '...<title>Plone site</title>...'

And on a content object with title::

    >>> browser.open(pageURL + '/@@plone.app.standardtiles.headtitle')
    >>> browser.contents
    '...<title>A simple page &#8212; Plone site</title>...'

The author link tile renders a link tag pointing to a page with info
about the creator of the context::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.authorlink')
    >>> browser.contents
    '...<link rel="author" href="http://nohost/plone/author/" title="Author information" />...'

The navigation link tile renders two links tags pointing to the site
root and the site map, respectively::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.navigationlink')
    >>> browser.contents
    '...<link rel="home" href="http://nohost/plone" title="Front page" />...<link rel="contents" href="http://nohost/plone/sitemap" title="Site Map" />...'

The search link tile renders a link tag pointing to the site search form::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.searchlink')
    >>> browser.contents
    '...<link rel="search" href="http://nohost/plone/search_form" title="Search this site" />...'

Footer tile::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.footer')
    >>> unprivileged_browser.contents
    '...id="portal-footer"...and the Plone logo are registered trademarks of the...'

Site actions tile::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.site_actions')
    >>> unprivileged_browser.contents
    '...id="portal-siteactions"...'

Empty analytics tile::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.analytics')
    >>> unprivileged_browser.contents
    '...<html><body></body></html>'

Now insert an example Google Analytics script::

    >>> snippet = "<script type='text/javascript'> var _gaq = _gaq || []; _gaq.push(['_setAccount', 'UA-XXXXX-X']); _gaq.push(['_trackPageview']); (function() { var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true; ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s); })();</script>"
    >>> from Products.CMFCore.utils import getToolByName
    >>> ptool = getToolByName(portal, "portal_properties")
    >>> ptool.site_properties.webstats_js = snippet
    >>> transaction.commit()
    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.analytics')
    >>> snippet in unprivileged_browser.contents
    True

Skip links tile::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.skip_links')
    >>> unprivileged_browser.contents
    '...class="hiddenStructure"...Skip to content...Skip to navigation...'

Test the personal bar as Anonymous::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.personal_bar')
    >>> unprivileged_browser.contents
    '...id="portal-personaltools-wrapper"...<a...Log in</a>...'

Also test the personal bar as a logged-in user::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.personal_bar')
    >>> browser.contents
    '...id="portal-personaltools-wrapper"...<a...Log out</a>...'

Logo tile::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.logo')
    >>> unprivileged_browser.contents
    '...id="portal-logo"...'

Global sections::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.global_sections')
    >>> unprivileged_browser.contents
    '...id="portal-globalnav"...'

Path bar tile::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.path_bar')
    >>> unprivileged_browser.contents
    '...id="portal-breadcrumbs"...'

Edit bar tile (test as logged in user)::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.edit_bar')
    >>> browser.contents
    '...id="content-views"...'

Should also contain content actions (test as logged in user)::

    >>> browser.contents
    '...id="contentActionMenus"...'

Document byline tile (test as logged in user)::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.document_byline')
    >>> browser.contents
    '...id="plone-document-byline"...'

Table of contents tile::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.tableofcontents')
    >>> browser.contents
    '...id="document-toc"...'

Searchbox tile::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.searchbox')
    >>> unprivileged_browser.contents
    '...id="portal-searchbox"...'


Language selector tile
----------------------

The language selector tile shows a list of languages available in the
site. Since the language selection depends on cookies, this tile will
be only available if the corresponding setting is set in the
portal_languages tool.

By default, this setting set and the selector shows up::

    >>> lt = getToolByName(portal, 'portal_languages')
    >>> lt.use_cookie_negotiation
    True

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.languageselector')
    >>> browser.contents
    '...language-en...'

However, anonymous won't see the selector by default:

    >>> unprivileged_browser.open('/@@plone.app.standardtiles.languageselector')
    >>> 'language-en' in unprivileged_browser.contents
    False

But the ``always_show_selector`` flag is still obeyed::

    >>> lt.always_show_selector = True
    >>> transaction.commit()
    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.languageselector')
    >>> unprivileged_browser.contents
    '...language-en...'

Adding supported languages will show them in the tile::

    >>> lt.addSupportedLanguage('ca')
    >>> transaction.commit()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.languageselector')
    >>> browser.contents
    '...language-en...language-ca...'


Next/previous tile
------------------

The next previous tile shows a next and a previous button if there is
a next or a previous object. It can be activated by checking the checkbox
in the schema (edit).

Let's add a folder and add three pages for testing the tile::

    >>> portal.invokeFactory('Folder', 'next-previous-folder',
    ...     title='Next Previous folder')
    'next-previous-folder'
    >>> folder = portal.get('next-previous-folder')

    >>> folder.invokeFactory('Document', 'page-one', title='Page one')
    'page-one'
    >>> page1 = folder.get('page-one')

    >>> folder.invokeFactory('Document', 'page-two', title='Page two')
    'page-two'
    >>> page2 = folder.get('page-two')

    >>> folder.invokeFactory('Document', 'page-three', title='Page three')
    'page-three'
    >>> page3 = folder.get('page-three')


Test the tile on the first page. It should not be there since next
previous is still disabled (default configuration).

    >>> page1.restrictedTraverse('@@plone_nextprevious_view').enabled()
    False

    >>> tile_view = '@@plone.app.standardtiles.nextprevious'

    >>> html = page1.restrictedTraverse(tile_view)()
    >>> assert '<div' not in html, 'Next / previous is disabled ' + \
    ...     'but the tile has contents.'

Then we activate next previous and we should see a next-link when
rendering the tile on the first page::

    >>> folder.getField('nextPreviousEnabled').set(folder, True)
    >>> page1.restrictedTraverse('@@plone_nextprevious_view').enabled()
    True

    >>> html = page1.restrictedTraverse(tile_view)()
    >>> assert '<div' in html, 'Next / previous is enabled ' + \
    ...     'but the tiles is empty'
    >>> assert 'class="next"' in html, 'Expected "next" link'
    >>> assert 'class="previous"' not in html, 'Didn\'t expect "previous" link'

    >>> html = page2.restrictedTraverse(tile_view)()
    >>> assert '<div' in html, 'Next / previous is enabled ' + \
    ...     'but the tiles is empty'
    >>> assert 'class="next"' in html, 'Expected "next" link'
    >>> assert 'class="previous"' in html, 'Expected "previous" link'

    >>> html = page3.restrictedTraverse(tile_view)()
    >>> assert '<div' in html, 'Next / previous is enabled ' + \
    ...     'but the tiles is empty'
    >>> assert 'class="next"' not in html, 'Didn\'t expect "next" link'
    >>> assert 'class="previous"' in html, 'Expected "previous" link'

Cleanup::

    >>> portal.manage_delObjects(['next-previous-folder'])


Login tile
----------

For a logged-in user, the login tile should be empty::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.login')
    >>> print browser.contents
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
      <body>
      </body>
    </html>

When we are not logged in, we should get the form::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.login')
    >>> unprivileged_browser.contents
    '...id="loginform"...'

By default, we should not have the "register" link in there::

But if we enable self-registration, it should show up::

    >>> from plone.app.controlpanel.security import ISecuritySchema
    >>> security_settings = ISecuritySchema(portal)
    >>> security_settings.set_enable_self_reg(True)
    >>> transaction.commit()
    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.login')
    >>> unprivileged_browser.contents
    '...<a...@@register...New user...</a>...'


Configlets tile
---------------

The configlets tile renders a list of the available config dialogs::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.configlets')
    >>> browser.contents
    '...Site Setup...Add-ons...Calendar...Collections...'


Discussion tile
---------------

Add a discussion tile and add a comment thru this tile.

    >>> browser.open(pageURL + '/@@add-tile/plone.app.standardtiles.discussion/discussion-tile')
    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.discussion/discussion-pageURL')

    >>> 'You can add a comment by filling out the form below' in browser.contents
    True


Menu link tile
--------------

Add a menu_link tile:

    >>> browser.open(portalURL + '/@@add-tile/plone.app.standardtiles.menu_link/menu_link-tile')

    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.menu_link/menu_link-tile')

Currently the menu link only shows a 'manage page' link and some javascript:

    >>> """<a id="plone-cmsui-menu-link" href="http://nohost/plone/@@cmsui-menu">Manage page</a>""" in browser.contents
    True



