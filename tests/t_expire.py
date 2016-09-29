#!/usr/bin/env python
#
# Copyright 2011, Toru Maesaka
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.

import config
import time
import unittest
from kyototycoon import KyotoTycoon

class UnitTest(unittest.TestCase):
    def setUp(self):
        self.kt_http_handle = KyotoTycoon(binary=False)
        self.kt_http_handle.open(port=11978)

        self.kt_bin_handle = KyotoTycoon(binary=True)
        self.kt_bin_handle.open(port=11978)

        self.LARGE_KEY_LEN = 8000

    def tearDown(self):
        self.kt_http_handle.close()
        self.kt_bin_handle.close()

    def test_set_expire(self):
        self.assertTrue(self.kt_http_handle.clear())

        # Set record to be expired in 2 seconds.
        self.assertTrue(self.kt_http_handle.set('key1', 'value', 2))
        self.assertEqual(self.kt_http_handle.get('key1'), 'value')
        self.assertEqual(self.kt_http_handle.count(), 1)
        time.sleep(4)
        self.assertEqual(self.kt_http_handle.count(), 0)

        # Bulk expire in 2 seconds.
        self.assertTrue(self.kt_http_handle.set_bulk({'key1-1': 'value1', 'key1-2': 'value2'}, 2))
        self.assertEqual(self.kt_http_handle.get('key1-1'), 'value1')
        self.assertEqual(self.kt_http_handle.get('key1-2'), 'value2')
        self.assertEqual(self.kt_http_handle.count(), 2)
        time.sleep(4)
        self.assertEqual(self.kt_http_handle.count(), 0)

        # Set record to be expired in 2 seconds.
        self.assertTrue(self.kt_bin_handle.set('key2', 'value', 2))
        self.assertEqual(self.kt_bin_handle.get('key2'), 'value')
        self.assertEqual(self.kt_http_handle.count(), 1)
        time.sleep(4)
        self.assertEqual(self.kt_http_handle.count(), 0)

        # Bulk expire in 2 seconds.
        self.assertTrue(self.kt_bin_handle.set_bulk({'key2-1': 'value1', 'key2-2': 'value2'}, 2))
        self.assertEqual(self.kt_bin_handle.get('key2-1'), 'value1')
        self.assertEqual(self.kt_bin_handle.get('key2-2'), 'value2')
        self.assertEqual(self.kt_http_handle.count(), 2)
        time.sleep(4)
        self.assertEqual(self.kt_http_handle.count(), 0)

    def test_add_expire(self):
        self.assertTrue(self.kt_http_handle.clear())

        self.assertTrue(self.kt_http_handle.add('hello', 'world', 2))
        self.assertEqual(self.kt_http_handle.get('hello'), 'world')
        time.sleep(4)
        self.assertEqual(self.kt_http_handle.get('hello'), None)

if __name__ == '__main__':
    unittest.main()
