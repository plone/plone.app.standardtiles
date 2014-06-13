Field Tile
==========

A field tile is a very simple tile: it just displays a field of its context
honoring the widget customizations present in the schema tagged values; but it
doesn't take into account the other tagged values such as when to display
something or not, as this is both useless from a tile point-of-view, and causes
harm due to certain default settings of behaviours.

Let's then proceed and see how the field tile works. First of all, let's set up
a bit of boilerplate: ::

    >>> from plone.testing.z2 import Browser
    >>> app = layer['app']
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> content = layer['portal']['deco-test-type1']
    >>> import transaction

We now have a browser and a test content, which uses a very simple Dexterity
content type that has the following fields (see ``testing.py`` for details):

test_text
    A textline field

test_int
    An integer field

test_bool
    A boolean field

funky
    A textline field, with a funky custom widget

topsecret
    A textline field which needs view permissions

In addition to this, the object has the ``IDublinCore`` behaviour added.

The object has been created but its fields have not been edited yet.  In fact,
if we try to render the field tile of, say, the ``test_text`` field, we get an
empty field: ::

    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=test_text')
    >>> browser.contents
    '...<span id="form-widgets-test_text" ...></span>...'

Let's then edit the field: ::

    >>> content.test_text = u"Hello world"
    >>> transaction.commit()

And rerender the tile: ::

    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=test_text')
    >>> browser.contents
    '...<span id="form-widgets-test_text" ...>Hello world</span>...'

We can see that now the value is correwctly displayed. We can try the same
thing for the ``test_int`` and ``test_bool`` fields.
Initially they are void: ::

    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=test_int')
    >>> browser.contents
    '...<span id="form-widgets-test_int" ...></span>...'
    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=test_bool')
    >>> browser.contents
    '...<span id="form-widgets-test_bool" ...></span>...'

But if we edit them: ::

    >>> content.test_int = 10
    >>> content.test_bool = True
    >>> transaction.commit()

And look again at the tiles: ::

    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=test_int')
    >>> browser.contents
    '...<span id="form-widgets-test_int" ...>10</span>...'
    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=test_bool')
    >>> browser.contents
    '...<span id="form-widgets-test_bool" ... class="selected-option">Boolean test field...'

We see the values are there.

Custom widgets
--------------

Dexterity allows the developer not only to simply define a schema, but also to
annotate it in order to give "hints" to the various other components about what
to do in certain cases: one of these cases is how to display a form, and more
precisely the developer can annotate onto the schema a "hint" about which
widget to use.

The field tile honors this hint. The content type we are using has indeed a
field, ``funky``, which is a regular ``TextLine`` field with an annotation that
tells to render it using a widget that wraps the value inside an ``<h1>``
instead of a ``<span>``.

Let's begin by setting the value: ::

    >>> content.funky = u"Oh yeah, baby!"
    >>> transaction.commit()

And then looking up the relative field tile: ::

    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=funky')
    >>> browser.contents
    '...<h1 id="form-widgets-funky" class="funky-widget...>Oh yeah, baby!</h1>...'

Permissions
-----------

Another thing that can be hinted in schemas is field-level permissions. That
is, you might have a field within a schema that needs a special permission to
be viewed, a pewrmission that might be stricter than the permission neede to
view the object.

The ``topsecret`` field is an example, as you need to have the
``cmf.ModifyPortalContent`` permission to be able to see it. Let's first insert
some value into it: ::

    >>> content.topsecret = u"Santa Claus does not exist!"
    >>> transaction.commit()

And then let's try to invoke the tile via our browser. Let's keep in mind we
are logged out, so we should see an empty tile, because no value should be made
visible to normal user (which can be kids and really should not be spoiled
about Santa Claus' identity). ::

    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=topsecret')
    >>> browser.contents
    '...<html><body></body></html>...'

As we can see the tile is emp[ty and, after merging from the blocks engine,
will result in the field simply not being present.

If, however, we do log in as a user that has the right permissions: ::

    >>> from plone.app.standardtiles.tests.base import PASTANDARDTILES_TESTTYPE_FIXTURE
    >>> browser.open(layer['portal'].absolute_url() + '/login_form')
    >>> browser.getControl(name='__ac_name').value = PASTANDARDTILES_TESTTYPE_FIXTURE.EDITOR_USER_NAME
    >>> browser.getControl(name='__ac_password').value = PASTANDARDTILES_TESTTYPE_FIXTURE.EDITOR_USER_PASSWORD
    >>> browser.getControl(name='submit').click()

Now, we have the proper permissions so we should be able to see the highly
disruptive content of the field (which should not be public
knowledge at all): ::

    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=topsecret')
    >>> browser.contents
    '...<span id="form-widgets-topsecret" ...>Santa Claus does not exist!</span>...'

And let's now logout to not confuse following tests: ::

    >>> browser.open(layer['portal'].absolute_url() + '/logout')

Behavior fields
---------------

Right now, we have always operated on fields that were, in Dexterity terms,
onto the "main schema". But what about fields that are in behavior fields
associated to the content type?

The field tile can handle them aswell, although the name's prefixed with the
schema name (or dotted name, depending on the fact that collision occur or
not).

For example, the ``contributors`` field from the ``IDublinCore`` behavior has
been filled in. Let's try to display it: ::

    >>> browser.open(content.absolute_url() + '/@@plone.app.standardtiles.field?field=IDublinCore-contributors')
    >>> browser.contents
    '...<span id="form-widgets-contributors" ...>Jane Doe\nJohn Doe</span>...'

Andf we can see that the field is correctly displayed.
