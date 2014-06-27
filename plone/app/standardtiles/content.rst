=============
Content tiles
=============

Here we show up the main tiles used for the content usage.

First, we set up a browser instance and get Manager privileges::


Test set up
===========

    >>> from Products.CMFCore.utils import getToolByName
    >>> from plone.app.standardtiles.tests.base import EDITOR_USER_NAME
    >>> from plone.app.standardtiles.tests.base import EDITOR_USER_PASSWORD
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_NAME
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.locking.interfaces import ILockable
    >>> from plone.testing.z2 import Browser

    >>> import transaction

    >>> app = layer['app']
    >>> portal = layer['portal']
    >>> action_tool = getToolByName(portal, 'portal_actions')

    >>> portal_url = portal.absolute_url()
    >>> create_document_url = '{0}/createObject?type_name=Document'.format(portal_url)
    >>> page_id = 'a-simple-page'
    >>> page_url = '{0}/{1}'.format(portal_url, page_id)

    >>> base_tiles_url = '@@plone.app.standardtiles'
    >>> document_actions_tile_url = '{0}/{1}.document_actions'.format(portal_url, base_tiles_url)
    >>> keywords_tile_url = '{0}/{1}.keywords'.format(page_url, base_tiles_url)
    >>> related_items_tile_url = '{0}/{1}.related_items'.format(page_url, base_tiles_url)
    >>> history_tile_url = '{0}/{1}.history'.format(page_url, base_tiles_url)
    >>> lock_tile_url = '{0}/{1}.lockinfo'.format(page_url, base_tiles_url)


Browsers
--------

    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))

We also keep another testbrowser handy for testing how tiles are rendered if
you're not logged in::

    >>> unprivileged_browser = Browser(app)


Set roles
---------

    >>> setRoles(portal, TEST_USER_ID, ['Manager', ])
    >>> transaction.commit()  # make the browser see this role


Document creation
-----------------

We create a page in the site to use it in tests later::

    >>> browser.open(create_document_url)
    >>> browser.getControl(name='title').value = 'A simple page'
    >>> browser.getControl(name='description').value = 'A description'
    >>> browser.getControl('Save').click()
    >>> browser.url.endswith('a-simple-page')
    True


Document actions tile
=====================

The document actions tile just lists the actions registered
in the document_actions category.

We make sure at least the print action visibility is on::

    >>> print_action = action_tool.document_actions.get('print')
    >>> print_action
    <Action at /plone/portal_actions/document_actions/print>
    >>> print_action.visible = True
    >>> transaction.commit()

The print action shows up accordingly::

    >>> browser.open(document_actions_tile_url)
    >>> browser.contents
    '...id="document-action-print"...'


Keywords tile
-------------

The keywords tile displays a list of the keywords (aka subjects)
assigned to the context.

We will use the page we created before for the tests. Since we have
not added any keyword to it yet, the tile contents are empty::

    >>> browser.open(keywords_tile_url)
    >>> 'id="category"' in browser.contents
    False

If we now add some keywords to it::

    >>> browser.open('{0}/edit'.format(page_url))
    >>> browser.getControl(name='subject_keywords:lines').value = 'Statues\n Sprint'
    >>> browser.getControl('Save').click()

The tile will show them::

    >>> unprivileged_browser.open(keywords_tile_url)
    >>> unprivileged_browser.contents
    '...id="category"...Sprint...Statues...'


Related items tile
------------------

Add a related_items tile:

    >>> browser.open(related_items_tile_url)

We should add a relation thru 'page properties' but that functionality isn't here yet.
A relation must beadded to a deco page and tested if this tile shows that relation.

    >>> 'html for related items tile' in browser.contents
    True


History tile
------------

First edit a page so we have an edit history:

   >>> browser.open('{0}/edit'.format(page_url))
   >>> browser.getControl(name='title').value = 'A different title'
   >>> browser.getControl(label='Save').click()
   >>> 'A different title' in browser.contents
   True

Add a history tile on the page:

    >>> browser.open(history_tile_url)

Test if the edit action is visible in the viewlet:

    >>> '<span class="historyAction state-Edited">Edited</span>' in browser.contents
    True
    >>> 'versions_history_form?version_id=2#version_preview' in browser.contents
    True


Lock info tile
--------------

First lock the page::

    >>> page_obj = portal[page_id]
    >>> lockable = ILockable(page_obj)
    >>> lockable.lock()

Open the lock info tile:

    >>> browser.open(lock_tile_url)

We should see that the page is locked. But apparently the page isn't locked:

    >>> 'plone-lock-status' in browser.contents
    True
