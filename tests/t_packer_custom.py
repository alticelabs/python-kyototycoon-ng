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

class CustomPacker(object):
    prefix = '<data>'
    suffix = '</data>'

    def pack(self, data):
        data = self.prefix + data + self.suffix
        return data.encode('utf-8')

    def unpack(self, data):
        data = data[len(self.prefix):-len(self.suffix)]
        return data.decode('utf-8')

class UnitTest(unittest.TestCase):
    def setUp(self):
        self.kt_bin_handle = KyotoTycoon(binary=True, pack_type=kt_binary.KT_PACKER_CUSTOM,
                                                      custom_packer=CustomPacker())
        self.kt_bin_handle.open(port=11978)

        self.kt_http_handle = KyotoTycoon(binary=False, pack_type=kt_http.KT_PACKER_CUSTOM,
                                                        custom_packer=CustomPacker())
        self.kt_http_handle.open(port=11978)

    def tearDown(self):
        self.kt_bin_handle.close()
        self.kt_http_handle.close()

    def test_packer_bytes(self):
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

        self.assertTrue(self.kt_bin_handle.set('key1', 'abc'))
        self.assertEqual(self.kt_bin_handle.get('key1'), 'abc')

        self.assertTrue(self.kt_http_handle.set('key2', 'abcd'))
        self.assertEqual(self.kt_http_handle.get('key2'), 'abcd')

        self.assertTrue(self.kt_http_handle.append('key2', 'xyz'))
        self.assertEqual(self.kt_http_handle.get('key2'), 'abcdxyz')

        self.assertEqual(self.kt_http_handle.count(), 2)
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

if __name__ == '__main__':
    unittest.main()
