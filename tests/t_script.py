#!/usr/bin/env python
#
# Copyright 2014, Carlos Rodrigues
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.
#
# Kyoto Tycoon should be started like this:
#   $ ktserver -scr example/ktscrex.lua '%'

import config
import unittest
from kyototycoon import KyotoTycoon

class UnitTest(unittest.TestCase):
    def setUp(self):
        self.kt_http_handle = KyotoTycoon(binary=False)
        self.kt_http_handle.open(port=11978)

        self.kt_bin_handle = KyotoTycoon(binary=True)
        self.kt_bin_handle.open(port=11978)

    def tearDown(self):
        self.kt_http_handle.close()
        self.kt_bin_handle.close()

    def test_play_script(self):
        self.assertTrue(self.kt_http_handle.clear())
        self.assertEqual(self.kt_http_handle.count(), 0)

        self.assertEqual(self.kt_bin_handle.play_script('echo', {'key1': b'abc'}), {'key1': b'abc'})

        self.assertEqual(self.kt_bin_handle.play_script('set', {'key': b'key2', 'value': b'abcd'}), {})
        out = self.kt_bin_handle.play_script('get', {'key': b'key2'})
        self.assertTrue('value' in out)
        self.assertEqual(out['value'], b'abcd')

        self.assertEqual(self.kt_http_handle.play_script('echo', {'key3': b'abc'}), {'key3': b'abc'})

        self.assertEqual(self.kt_http_handle.play_script('set', {'key': b'key4', 'value': b'abcd'}), {})
        out = self.kt_http_handle.play_script('get', {'key': b'key4'})
        self.assertTrue('value' in out)
        self.assertEqual(out['value'], b'abcd')


if __name__ == '__main__':
    unittest.main()
