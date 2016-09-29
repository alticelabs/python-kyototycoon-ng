#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Carlos Rodrigues
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.

import config
import unittest
from kyototycoon import KyotoTycoon

import kyototycoon.kt_http as kt_http
import kyototycoon.kt_binary as kt_binary

class UnitTest(unittest.TestCase):
    def setUp(self):
        self.kt_bin_handle = KyotoTycoon(binary=True, pack_type=kt_binary.KT_PACKER_BYTES)
        self.kt_bin_handle.open(port=11978)

        self.kt_http_handle = KyotoTycoon(binary=False, pack_type=kt_http.KT_PACKER_BYTES)
        self.kt_http_handle.open(port=11978)

    def tearDown(self):
        self.kt_bin_handle.close()
        self.kt_http_handle.close()

    def test_packer_bytes(self):
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

        value1 = bytes([0x00, 0x01, 0x02, 0xff])
        self.assertTrue(self.kt_bin_handle.set('key1', value1))
        value2 = self.kt_bin_handle.get('key1')
        self.assertEqual(value1, value2)
        self.assertEqual(type(value1), type(value2))

        value3 = bytes([0x00, 0x01, 0x03, 0xff])
        self.assertTrue(self.kt_http_handle.set('key2', value3))
        value4 = self.kt_http_handle.get('key2')
        self.assertEqual(value3, value4)
        self.assertEqual(type(value3), type(value4))

        self.assertTrue(self.kt_http_handle.append('key2', 'xyz'))
        self.assertEqual(self.kt_http_handle.get('key2'), value3 + b'xyz')

        self.assertEqual(self.kt_http_handle.count(), 2)
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

if __name__ == '__main__':
    unittest.main()
