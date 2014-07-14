# -*- coding: utf-8 -*-
from plone.app.standardtiles.tests.base import \
    PASTANDARDTILES_FUNCTIONAL_TESTING
from plone.app.standardtiles.tests.base import \
    PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import pprint
import unittest2 as unittest

try:
    import interlude
    interlude_interact = interlude.interact
except ImportError:
    # interlude is only a development requirement
    interlude_interact = None


optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
normal_testfiles = [
    '../content.rst',
    '../media.rst',
    '../layout.rst',
    '../head.rst',
]
testtype_testfiles = [
    '../field.rst',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test,
                                     optionflags=optionflags,
                                     globs={'interact': interlude_interact,
                                            'pprint': pprint.pprint,
                                            },
                                     ),
                layer=PASTANDARDTILES_FUNCTIONAL_TESTING)
        for test in normal_testfiles])
    suite.addTests([
        layered(doctest.DocFileSuite(test,
                                     optionflags=optionflags,
                                     globs={'interact': interlude_interact,
                                            'pprint': pprint.pprint,
                                            },
                                     ),
                layer=PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING)
        for test in testtype_testfiles])
    return suite
