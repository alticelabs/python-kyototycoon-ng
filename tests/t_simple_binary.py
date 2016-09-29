#!/usr/bin/env python
#
# Copyright 2011, Toru Maesaka
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.

import config
import unittest
from kyototycoon import KyotoTycoon
from kyototycoon.kt_binary import KT_PACKER_PICKLE

class UnitTest(unittest.TestCase):
    def setUp(self):
        # For operations not supported by the binary protocol, but useful for testing it...
        self.kt_handle_http = KyotoTycoon(binary=False)
        self.kt_handle_http.open(port=11978)

        self.kt_handle = KyotoTycoon(binary=True, pack_type=KT_PACKER_PICKLE)
        self.kt_handle.open(port=11978)
        self.LARGE_KEY_LEN = 8000

    def tearDown(self):
        self.kt_handle_http.close()
        self.kt_handle.close()

    def test_set(self):
        self.assertTrue(self.kt_handle_http.clear())

        self.assertTrue(self.kt_handle.set('key', 'value'))

        self.assertTrue(self.kt_handle.set('k e y', 'v a l u e'))
        self.assertTrue(self.kt_handle.set('k\te\ty', 'tabbed'))

        self.assertEqual(self.kt_handle.get('key'), 'value')
        self.assertEqual(self.kt_handle.get('k e y'), 'v a l u e')
        self.assertEqual(self.kt_handle.get('k\te\ty'), 'tabbed')

        self.assertTrue(self.kt_handle.set('\\key', '\\xxx'))
        self.assertEqual(self.kt_handle.get('\\key'), '\\xxx')
        self.assertEqual(self.kt_handle_http.count(), 4)

        self.assertTrue(self.kt_handle.set('tabbed\tkey', 'tabbled\tvalue'))
        self.assertTrue(self.kt_handle.get('tabbed\tkey'))

        self.assertTrue(self.kt_handle.set('url1', 'http://github.com'))
        self.assertTrue(self.kt_handle.set('url2', 'https://github.com/'))
        self.assertTrue(self.kt_handle.set('url3', 'https://github.com/blog/'))

        self.assertTrue(self.kt_handle.set('http://github.com', 'url1'))
        self.assertTrue(self.kt_handle.set('https://github.com', 'url2'))
        self.assertTrue(self.kt_handle.set('https://github.com/blog/', 'url3'))

        self.assertEqual(self.kt_handle.get('non_existent'), None)

        self.assertTrue(self.kt_handle.set('cb', 1791))
        self.assertEqual(self.kt_handle.get('cb'), 1791)

        self.assertTrue(self.kt_handle.set('cb', 1791.1226))
        self.assertEqual(self.kt_handle.get('cb'), 1791.1226)

    def test_remove(self):
        self.assertTrue(self.kt_handle_http.clear())

        self.assertFalse(self.kt_handle.remove('must fail key'))
        self.assertTrue(self.kt_handle.set('deleteable key', 'xxx'))
        self.assertTrue(self.kt_handle.remove('deleteable key'))

    def test_set_bulk(self):
        self.assertTrue(self.kt_handle_http.clear())

        dict = {
            'k1': 'one',
            'k2': 'two',
            'k3': 'three',
            'k4': 'four',
            'k\n5': 'five',
            'k\t6': 'six',
            'k7': 111
        }

        n = self.kt_handle.set_bulk(dict, atomic=False)
        self.assertEqual(len(dict), n)
        self.assertEqual(self.kt_handle.get('k1'), 'one')
        self.assertEqual(self.kt_handle.get('k2'), 'two')
        self.assertEqual(self.kt_handle.get('k3'), 'three')
        self.assertEqual(self.kt_handle.get('k4'), 'four')
        self.assertEqual(self.kt_handle.get('k\n5'), 'five')
        self.assertEqual(self.kt_handle.get('k\t6'), 'six')
        self.assertEqual(self.kt_handle.get('k7'), 111)

        d = self.kt_handle.get_bulk(['k1', 'k2', 'k3', 'k4',
                                     'k\n5', 'k\t6', 'k7'], atomic=False)

        self.assertEqual(len(d), len(dict))
        self.assertEqual(d, dict)

        self.assertEqual(self.kt_handle_http.count(), 7)
        n = self.kt_handle.remove_bulk(['k1', 'k2', 'k\t6'], atomic=False)
        self.assertEqual(self.kt_handle_http.count(), 4)
        n = self.kt_handle.remove_bulk(['k3'], atomic=False)
        self.assertEqual(self.kt_handle_http.count(), 3)

    def test_get_bulk(self):
        self.assertTrue(self.kt_handle_http.clear())
        self.assertTrue(self.kt_handle.set('a', 'one'))
        self.assertTrue(self.kt_handle.set('b', 'two'))
        self.assertTrue(self.kt_handle.set('c', 'three'))
        self.assertTrue(self.kt_handle.set('d', 'four'))

        d = self.kt_handle.get_bulk(['a','b','c','d'], atomic=False)
        assert d is not None

        self.assertEqual(d['a'], 'one')
        self.assertEqual(d['b'], 'two')
        self.assertEqual(d['c'], 'three')
        self.assertEqual(d['d'], 'four')
        self.assertEqual(len(d), 4)

        d = self.kt_handle.get_bulk(['a','x','y','d'], atomic=False)
        self.assertEqual(len(d), 2)
        d = self.kt_handle.get_bulk(['w','x','y','z'], atomic=False)
        self.assertEqual(len(d), 0)
        d = self.kt_handle.get_bulk([], atomic=False)
        self.assertEqual(d, {})

    def test_large_key(self):
        large_key = 'x' * self.LARGE_KEY_LEN
        self.assertTrue(self.kt_handle.set(large_key, 'value'))
        self.assertEqual(self.kt_handle.get(large_key), 'value')


if __name__ == '__main__':
    unittest.main()
