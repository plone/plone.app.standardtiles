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

Most of these tiles should (also) be available to Anonymous users::

    >>> unprivileged_browser = Browser(app)

Title::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.headtitle')
    >>> unprivileged_browser.contents
    '...<head...<title...>...</title>...</head>...'

Stylesheets::

    >>> unprivileged_browser.open(portalURL + '/@@plone.app.standardtiles.stylesheets')
    >>> unprivileged_browser.contents
    '...<head...<link.../>...</head>...'

Javascripts::

    >>> unprivileged_browser.open(portalURL +'/@@plone.app.standardtiles.javascripts')
    >>> unprivileged_browser.contents
    '...<head...<script...>...</script>...</head>...'

Favicon link::

    >>> unprivileged_browser.open(portalURL +'/@@plone.app.standardtiles.faviconlink')
    >>> unprivileged_browser.contents
    '...<head...<link...favicon.ico.../>...</head>...'

Search link::

    >>> unprivileged_browser.open(portalURL +'/@@plone.app.standardtiles.searchlink')
    >>> unprivileged_browser.contents
    '...<head...<link rel="search".../>...</head>...'

Navigation link::

    >>> unprivileged_browser.open(portalURL +'/@@plone.app.standardtiles.navigationlink')
    >>> unprivileged_browser.contents
    '...<head...<link rel="home".../>...</head>...'
    >>> unprivileged_browser.contents
    '...<head...<link rel="contents".../>...</head>...'

RSS link::

    >>> unprivileged_browser.open(portalURL +'/@@plone.app.standardtiles.rsslink')
    >>> unprivileged_browser.contents
    '...<head...<link ... type="application/rss+xml" />...</head>...'

Canonical URL link::

    >>> unprivileged_browser.open(portalURL +'/@@plone.app.standardtiles.canonical_url')
    >>> unprivileged_browser.contents
    '...<head...<link rel="canonical".../>...</head>...'

Author link::

    >>> browser.open(portalURL + '/@@plone.app.standardtiles.authorlink')
    >>> browser.contents
    '...<head...<link rel="author".../>...</head>...'
