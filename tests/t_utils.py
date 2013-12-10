#!/usr/bin/env python
#
# Copyright 2011, Toru Maesaka
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.

import config
import unittest
import kyototycoon.kt_http

class UnitTest(unittest.TestCase):
    def setUp(self):
        self.kt_core = kyototycoon.kt_http.ProtocolHandler()

    def test_packer(self):
        stri = 'hello world sir'
        buf = self.kt_core._pickle_packer(stri)
        if type(stri) is str:
            assert buf == stri
        else:
            assert buf != stri
        ret = self.kt_core._pickle_unpacker(buf)
        self.assertEqual(stri, ret)

        num = 777
        buf = self.kt_core._pickle_packer(num)
        assert buf != num
        ret = self.kt_core._pickle_unpacker(buf)
        self.assertEqual(type(num), type(ret))
        self.assertEqual(num, ret)

if __name__ == '__main__':
    unittest.main()
