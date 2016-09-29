#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015, Carlos Rodrigues
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.

#
# This test does not require a KT server with the memcache protocol enabled.
#

import config
import unittest

from kyototycoon import KyotoTycoon
from kyototycoon.packers import SimpleMemcachePacker

import kyototycoon.kt_http as kt_http
import kyototycoon.kt_binary as kt_binary

class UnitTest(unittest.TestCase):
    def setUp(self):
        memc_packer = SimpleMemcachePacker()

        self.kt_bin_handle = KyotoTycoon(binary=True, pack_type=kt_binary.KT_PACKER_CUSTOM,
                                                      custom_packer=memc_packer)
        self.kt_bin_handle.open(port=11978)

        self.kt_http_handle = KyotoTycoon(binary=False, pack_type=kt_http.KT_PACKER_CUSTOM,
                                                        custom_packer=memc_packer)
        self.kt_http_handle.open(port=11978)

    def tearDown(self):
        self.kt_bin_handle.close()
        self.kt_http_handle.close()

    def test_packer_bin(self):
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

        self.assertTrue(self.kt_bin_handle.set('key1-1', (b'12345', 1234)))
        self.assertEqual(self.kt_bin_handle.get('key1-1'), (b'12345', 1234))

        self.assertRaises(ValueError, self.kt_bin_handle.set, 'key1-2', (b'12345', -1))

        self.assertEqual(self.kt_http_handle.count(), 1)
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

    def test_packer_http(self):
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

        self.assertTrue(self.kt_http_handle.set('key2-1', (b'12345', 1234)))
        self.assertEqual(self.kt_http_handle.get('key2-1'), (b'12345', 1234))

        self.assertRaises(ValueError, self.kt_http_handle.set, 'key2-2', (b'12345', -1))

        self.assertEqual(self.kt_http_handle.count(), 1)
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

if __name__ == '__main__':
    unittest.main()
