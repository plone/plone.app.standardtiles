# -*- coding: utf-8 -*-
from lxml import html
from plone.app.standardtiles.testing import EDITOR_USER_NAME
from plone.app.standardtiles.testing import EDITOR_USER_PASSWORD
from plone.app.standardtiles.testing import PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING  # noqa
from plone.testing.z2 import Browser
from unittest import TestCase
import transaction

def fromstring(s):
    html_parser = html.HTMLParser(encoding='utf-8')
    return html.fromstring(s, parser=html_parser).getroottree().getroot()


class TestFieldTile(TestCase):
    """A field tile is a very simple tile: it just displays a field of its
    context honoring the widget customizations present in the schema tagged
    values; but it doesn't take into account the other tagged values such as
    when to display something or not, as this is both useless from a tile
    point-of-view, and causes harm due to certain default settings of
    behaviours.

    """
    layer = PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING

    def setUp(self):
        """We have a browser and a test content, which uses a very simple
        Dexterity content type that has the following fields (see
        ``testing.py`` for details):

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

        In addition to this, the object has the ``IDublinCore`` behaviour
        added.

        """
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.content = self.layer['portal']['deco-test-type1']

    def test_text_field(self):
        """The object has been created but its fields have not been edited yet.
        In fact, if we try to render the field tile of, say, the ``test_text``
        field, we get an empty field:

        """
        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=test_text'
        )
        self.assertIn('<span id="form-widgets-test_text"',
                      self.browser.contents)
        self.assertNotIn('>Hello world</span>',
                         self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="form-widgets-test_text"]')
        self.assertEqual(len(nodes), 1)
        self.assertIsNone(nodes[0].text)

        # Let's then edit the field:
        self.content.test_text = u"Hello world"
        transaction.commit()

        # And rerender the tile:
        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=test_text'
        )
        self.assertIn('<span id="form-widgets-test_text"',
                      self.browser.contents)
        self.assertIn('>Hello world</span>',
                      self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="form-widgets-test_text"]')
        self.assertEqual(len(nodes), 1)
        self.assertEqual(u'Hello world', nodes[0].text)

    def test_int_field(self):
        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=test_int'
        )
        self.assertIn('<span id="form-widgets-test_int"',
                      self.browser.contents)
        self.assertNotIn('>10</span>',
                         self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="form-widgets-test_int"]')
        self.assertEqual(len(nodes), 1)
        self.assertIsNone(nodes[0].text)

        # Let's then edit the field:
        self.content.test_int = 10
        transaction.commit()

        # And rerender the tile:
        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=test_int'
        )
        self.assertIn('<span id="form-widgets-test_int"',
                      self.browser.contents)
        self.assertIn('>10</span>',
                      self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="form-widgets-test_int"]')
        self.assertEqual(len(nodes), 1)
        self.assertEqual('10', nodes[0].text)

    def test_bool_field(self):
        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=test_bool'
        )
        self.assertIn('<span id="form-widgets-test_bool"',
                      self.browser.contents)
        self.assertNotIn('class="selected-option"',
                         self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="form-widgets-test_bool"]')
        self.assertEqual(len(nodes), 1)
        self.assertEqual(0, len(nodes[0].getchildren()))

        # Let's then edit the field:
        self.content.test_bool = True
        transaction.commit()

        # And rerender the tile:
        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=test_bool'
        )
        self.assertIn('<span id="form-widgets-test_bool"',
                      self.browser.contents)
        self.assertIn('class="selected-option"',
                      self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="form-widgets-test_bool"]')
        self.assertEqual(len(nodes), 1)

        children = nodes[0].xpath('//*[@class="selected-option"]')
        self.assertEqual(1, len(children))

    def test_custom_widget(self):
        """Dexterity allows the developer not only to simply define a schema,
        but also to annotate it in order to give "hints" to the various other
        components about what to do in certain cases: one of these cases is how
        to display a form, and more precisely the developer can annotate onto
        the schema a "hint" about which widget to use.

        The field tile honors this hint. The content type we are using has
        indeed a field, ``funky``, which is a regular ``TextLine`` field with
        an annotation that tells to render it using a widget that wraps the
        value inside an ``<h1>`` instead of a ``<span>``.

        """
        # Let's begin by setting the value:
        self.content.funky = u"Oh yeah, baby!"
        transaction.commit()

        # And then looking up the relative field tile:
        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=funky'
        )
        self.assertIn('<h1 id="form-widgets-funky" class="funky-widget',
                      self.browser.contents)
        self.assertIn('>Oh yeah, baby!</h1>',
                      self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//h1[@id="form-widgets-funky"]')
        self.assertEqual(len(nodes), 1)
        self.assertIn('funky-widget', nodes[0].attrib['class'].split())
        self.assertEqual('Oh yeah, baby!', nodes[0].text)

    def test_permissions(self):
        """Another thing that can be hinted in schemas is field-level
        permissions. That is, you might have a field within a schema that needs
        a special permission to be viewed, a pewrmission that might be stricter
        than the permission neede to view the object.

        The ``topsecret`` field is an example, as you need to have the
        ``cmf.ModifyPortalContent`` permission to be able to see it.

        """
        # Let's first insert some value into it:
        self.content.topsecret = u"Santa Claus does not exist!"
        transaction.commit()

        # And then let's try to invoke the tile via our browser. Let's keep
        # in mind we are logged out, so we should see an empty tile, because no
        # value should be made visible to normal user (which can be kids and
        # really should not be spoiled about Santa Claus' identity).

        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=topsecret'
        )
        self.assertEqual('<html></html>', self.browser.contents)

        # As we can see the tile is emp[ty and, after merging from the blocks
        # engine, will result in the field simply not being present.
        self.browser.open(self.layer['portal'].absolute_url() + '/login_form')
        self.browser.getControl(name='__ac_name').value = EDITOR_USER_NAME
        self.browser.getControl(name='__ac_password').value = EDITOR_USER_PASSWORD  # noqa
        self.browser.getControl(name='submit').click()

        # Now, we have the proper permissions so we should be able to see the
        # highly disruptive content of the field (which should not be public
        # knowledge at all): ::

        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=topsecret'
        )
        self.assertIn('<span id="form-widgets-topsecret"',
                      self.browser.contents)
        self.assertIn('>Santa Claus does not exist!</span>',
                      self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="form-widgets-topsecret"]')
        self.assertEqual(len(nodes), 1)
        self.assertEqual('Santa Claus does not exist!', nodes[0].text)

    def test_behavior_field(self):
        """Right now, we have always operated on fields that were, in Dexterity
        terms, onto the "main schema". But what about fields that are in
        behavior fields associated to the content type?

        The field tile can handle them as well, although the name's prefixed
        with the schema name (or dotted name, depending on the fact that
        collision occur or not).

        For example, the ``contributors`` field from the ``IDublinCore``
        behavior has been filled in. Let's try to display it:

        """
        self.browser.open(
            self.content.absolute_url()
            + '/@@plone.app.standardtiles.field?field=IDublinCore-contributors')  # noqa
        self.assertIn('<span id="form-widgets-IDublinCore-contributors"',
                      self.browser.contents)
        self.assertIn('>Jane Doe;John Doe</span>',
                      self.browser.contents)

        root = fromstring(self.browser.contents)
        nodes = root.xpath('//body//*[@id="form-widgets-IDublinCore-contributors"]')  # noqa
        self.assertEqual(len(nodes), 1)
        self.assertEqual('Jane Doe;John Doe', nodes[0].text)
