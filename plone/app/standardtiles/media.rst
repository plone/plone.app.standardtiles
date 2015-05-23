Media tiles
===========

Here we introduce and exercise some tiles like navigation, proxy or
embed.

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


Embed tile
----------

The embed tile is a transient tile which takes a media URL
and displays the associated embedded code::

    >>> browser.open(portalURL+ '/@@add-tile/plone.app.standardtiles.embed/embed-tile')
    >>> browser.getControl(name='media_url').value = 'http://www.youtube.com/watch?v=ayPKvFNz8aE'
    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.embed/embed-tile')
    >>> browser.contents
    '<html><body><object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/ayPKvFNz8aE&hl=en_GB&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/ayPKvFNz8aE&hl=en_GB&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object></body></html>'


Proxy tile
----------

The proxy tile takes the int id of a content object in the site and
displays the result of calling ``@@proxy-view`` on it. The default
``@@proxy-view``, registered for all interfaces, renders the contents
of the ``#content`` HTML element of the default view of the object.

Using the proxy tile with the document we formerly created exhibits the default behavior::

    >>> browser.open(portalURL + '/@@add-tile/plone.app.standardtiles.proxy/proxy-tile')
    >>> browser.getControl(name='contentId.widgets.query').value = 'A simple page'
    >>> browser.getControl(name='contentId.buttons.search').click()
    >>> contentId = browser.getControl(name="contentId:list")
    >>> contentId.displayOptions
    ['A simple page']
    >>> contentId.getControl('A simple page').selected = True
    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.proxy/proxy-tile')
    >>> browser.contents
    '...id="content"...A simple page...A description...'

If we register a view with the name ``@@proxy-view`` for a more
specific interface, it will be used instead::

    >>> from zope.interface import Interface
    >>> from Products.ATContentTypes.interfaces.document import IATDocument
    >>> from zope.component import adapts, provideAdapter
    >>> from Products.Five.browser import BrowserView
    >>> from zope.publisher.interfaces.browser import IBrowserView

    >>> class ProxyView(BrowserView):
    ...     adapts(IATDocument, Interface)
    ...     def __call__(self):
    ...         return "Custom proxy view."
    >>> provideAdapter(ProxyView, provides=IBrowserView, name="proxy-view")

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.proxy/proxy-tile')
    >>> browser.contents
    'Custom proxy view.'


Navigation tree tile
--------------------

The navigation tree tile displays a navigation tree for the context
where it's inserted and take no configuration parameters.

Rendering this tile in the site root should show the document we
created before::

    >>> browser.open(portalURL + '/@@add-tile/plone.app.standardtiles.navigation/navigation-tile')
    >>> browser.getControl(name='name').value = 'TEST NAVIGATION TILE'
    >>> browser.getControl(name='includeTop:list').value = ['selected']
    >>> browser.getControl(name='topLevel').value = '0'
    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.navigation/navigation-tile')
    >>> print browser.contents
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
      <body>
        <div class="navigationTile">
          <h2 class="tileHeader">TEST NAVIGATION TILE</h2>
          <ul class="navTree navTreeLevel0">
            <li class="navTreeItem navTreeTopNode navTreeCurrentNode">
    <BLANKLINE>
                <a href="http://nohost/plone" class="contenttype-plone-site navTreeCurrentItem" title="">
                  <span>Home</span></a>
    <BLANKLINE>
            </li>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <li class="navTreeItem visualNoMarker section-a-simple-page">
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
            <a href="http://nohost/plone/a-simple-page" class="state-missing-value contenttype-document" title="A description">
    <BLANKLINE>
                <span>A simple page</span></a>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    </li>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
          </ul>
        </div>
      </body>
    </html>
    <BLANKLINE>

Sitemap tree tile
-----------------

The sitemap tile displays a sitemap for the site.

Rendering this tile in the site root should show the document we
created before::

    >>> browser.open(portalURL + '/@@add-tile/plone.app.standardtiles.sitemap/sitemap-tile')
    >>> browser.getControl(name='name').value = 'TEST SITEMAP TILE'
    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.sitemap/sitemap-tile')
    >>> print browser.contents
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
      <body>
        <div class="navigationTile">
          <ul class="navTree navTreeLevel0">
            <li class="navTreeItem navTreeTopNode navTreeCurrentNode">
                <a href="http://nohost/plone" class="contenttype-plone-site navTreeCurrentItem" title="">
                  <span>Home</span></a>
            </li>
            <li class="navTreeItem visualNoMarker section-a-simple-page">
                    <a href="http://nohost/plone/a-simple-page" class="state-missing-value contenttype-document" title="A description">
                  <span>A simple page</span></a>
            </li>
          </ul>
        </div>
      </body>
    </html>


Attachment tile
---------------

This persistent tile renders a link pointing to a file stored in the
tile data itself.

Since the attachment file uses the plone.formwidget.multifile, wich bases
on flash, we cannot test it with our test browser. So we need to remove
the widget and then test it with the MultiWidget / NamedFileWidget.

    >>> from plone.app.standardtiles import attachment
    >>> del attachment.IAttachmentTile._Element__tagged_values['plone.autoform.widgets']['files']

    >>> browser.open(portalURL + '/@@add-tile/plone.app.standardtiles.attachment/attachment-tile')
    >>> browser.getControl(name='files.buttons.add').click()
    >>> upload = browser.getControl(name='files.0')
    >>> import cStringIO
    >>> upload.add_file(cStringIO.StringIO('File contents'), 'text/plain', 'textfile.txt')
    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.attachment/attachment-tile')
    >>> html = browser.contents
    >>> html
    '...<a href="http://nohost/plone/@@plone.app.standardtiles.attachment/attachment-tile/@@download/0">...<img class="icon" src="http://nohost/plone/txt.png" alt="" />...textfile.txt...Plain Text...'

We should also be able to download the file::

    >>> browser.open(portalURL + \
    ...     '/@@plone.app.standardtiles.attachment/attachment-tile/@@download/0')
    >>> browser.contents
    'File contents'


Calendar tile
-------------

This tile shows a calendar.

    >>> browser.open(portalURL + '/@@add-tile/plone.app.standardtiles.calendar/calendar-tile')
    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.calendar/calendar-tile')
    >>> browser.contents
    '...<dl class="calendar-tile"...'

If we create a new event the cache should be invalidated::

    >>> tile = portal.unrestrictedTraverse(
    ...     '@@plone.app.standardtiles.calendar/calendar-tile')
    >>> 'ACTUAL_URL' not in portal.REQUEST.keys()
    True
    >>> portal.REQUEST['ACTUAL_URL'] = portalURL + \
    ...     '/@@plone.app.standardtiles.calendar/calendar-tile'
    >>> prior_html = tile()
    >>> from DateTime import DateTime

Lets a event in the last day of the current month::

    >>> year, month = tile.getYearAndMonthToDisplay()
    >>> year, month = tile.getNextMonth(year, month)
    >>> last_day_month = DateTime('%s/%s/1' % (year, month)) - 1
    >>> hour = 1 / 24.0
    >>> portal.invokeFactory('Event', 'e1',
    ...     startDate=last_day_month + 23 * hour,
    ...     endDate=last_day_month + 23.5 * hour)
    'e1'
    >>> portal.e1
    <ATEvent at /plone/e1>

We also need to publish it. But the default workflow may not
be set beause of a unknown problem with the test:

    >>> portal.portal_workflow.setDefaultChain('simple_publication_workflow')
    >>> portal.portal_workflow.doActionFor(portal.e1, 'publish')
    >>> portal.portal_workflow.getInfoFor(portal.e1, 'review_state')
    'published'

Rendering the tile again should result in different html:

     >>> assert prior_html != tile(), "Cache key wasn't invalidated"
     >>> 'class="event"' in tile()
     True


RSS Tile
--------

This tile shows the first five items in a RSS feed.

Use the RSS stored in the test directory, this way we don't have an external dependency.

    >>> import os
    >>> import plone.app.standardtiles.tests as test_dir
    >>> test_dir = os.path.dirname(test_dir.__file__)
    >>> path = 'file://{0}'.format(os.path.join(test_dir, 'RSS.xml'))

Create the RSS tile, with the local RSS URI:

    >>> browser.open(portalURL + '/@@add-tile/plone.app.standardtiles.rss/rss-tile')
    >>> browser.getControl(name='portlet_title').value = 'TEST RSS TILE'
    >>> browser.getControl(name='url').value = path
    >>> browser.getControl(label='Save').click()
    >>> browser.open(portalURL + '/@@plone.app.standardtiles.rss/rss-tile')
    >>> 'TEST RSS TILE' in browser.contents
    True
    >>> """<a href="http://localhost:55440/plone/doc-one" class="tile">""" in browser.contents
    True
