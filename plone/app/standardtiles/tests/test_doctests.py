import doctest
from plone.testing import layered
import unittest2 as unittest
from base import PASTANDARDTILES_FUNCTIONAL_TESTING
import pprint
import interlude

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
testfiles = [
    '../standardtiles.txt',
    '../field.txt',
]
def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test ,
                                     optionflags=optionflags,
                                     globs={'interact': interlude.interact,
                                            'pprint': pprint.pprint,
                                            }
                                     ),
                layer=PASTANDARDTILES_FUNCTIONAL_TESTING)
        for test in testfiles])
    return suite
