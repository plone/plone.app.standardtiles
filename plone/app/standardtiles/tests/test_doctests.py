# -*- coding: utf-8 -*-
from plone.app.standardtiles.tests.base import \
    PASTANDARDTILES_FUNCTIONAL_TESTING
from plone.app.standardtiles.tests.base import \
    PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import interlude
import pprint
import unittest2 as unittest


optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
normal_testfiles = [
    '../content.txt',
    '../media.txt',
    '../layout.txt',
    '../head.txt',
]
testtype_testfiles = [
    '../field.txt',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test,
                                     optionflags=optionflags,
                                     globs={'interact': interlude.interact,
                                            'pprint': pprint.pprint,
                                            },
                                     ),
                layer=PASTANDARDTILES_FUNCTIONAL_TESTING)
        for test in normal_testfiles])
    suite.addTests([
        layered(doctest.DocFileSuite(test,
                                     optionflags=optionflags,
                                     globs={'interact': interlude.interact,
                                            'pprint': pprint.pprint,
                                            },
                                     ),
                layer=PASTANDARDTILES_TESTTYPE_FUNCTIONAL_TESTING)
        for test in testtype_testfiles])
    return suite
