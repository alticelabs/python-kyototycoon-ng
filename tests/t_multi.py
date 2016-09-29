#!/usr/bin/env python
#
# Copyright 2011, Toru Maesaka
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.
#
# Kyoto Tycoon should be started like this:
#   $ ktserver one.kch two.kch

import config
import time
import unittest
from kyototycoon import KyotoTycoon, KyotoTycoonException

DB_1 = 0
DB_2 = 1
DB_INVALID = 3

class UnitTest(unittest.TestCase):
    def setUp(self):
        self.kt_handle_http = KyotoTycoon(binary=False)
        self.kt_handle_http.open(port=11978)

        self.kt_handle_bin = KyotoTycoon(binary=True)
        self.kt_handle_bin.open(port=11978)

        self.LARGE_KEY_LEN = 8000

    def tearDown(self):
        self.kt_handle_http.close()
        self.kt_handle_bin.close()

    def clear_all(self):
        self.assertTrue(self.kt_handle_http.clear(db=DB_1))
        self.assertTrue(self.kt_handle_http.clear(db=DB_2))
        return True

    def test_status(self):
        status = self.kt_handle_http.status(DB_1)
        assert status is not None

        status = self.kt_handle_http.status(DB_2)
        assert status is not None

        self.assertRaises(KyotoTycoonException, self.kt_handle_http.status, DB_INVALID)
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.status, 'non_existent')

    def test_set_get(self):
        self.assertTrue(self.clear_all())
        self.assertTrue(self.kt_handle_http.set('ice', 'cream', db=DB_2))
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.set, 'palo', 'alto', db=DB_INVALID)

        self.assertEqual(self.kt_handle_http.get('ice'), None)
        self.assertEqual(self.kt_handle_http.get('ice', db=DB_1), None)
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.get, 'ice', db=DB_INVALID)

        self.assertEqual(self.kt_handle_http.get('ice', db=DB_2), 'cream')
        self.assertEqual(self.kt_handle_http.count(db=DB_1), 0)
        self.assertEqual(self.kt_handle_http.count(db=DB_2), 1)

        self.assertTrue(self.kt_handle_http.set('frozen', 'yoghurt', db=DB_1))
        self.assertEqual(self.kt_handle_http.count(db=DB_1), 1)

        self.assertEqual(self.kt_handle_http.get('frozen'), 'yoghurt')
        self.assertEqual(self.kt_handle_http.get('frozen', db=DB_1), 'yoghurt')
        self.assertEqual(self.kt_handle_http.get('frozen', db=DB_2), None)
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.get, 'frozen', db=DB_INVALID)

        self.assertTrue(self.kt_handle_http.clear(db=DB_1))
        self.assertEqual(self.kt_handle_http.count(db=DB_1), 0)
        self.assertEqual(self.kt_handle_http.count(db=DB_2), 1)

    def test_get_multi(self):
        self.assertTrue(self.clear_all())

        self.assertTrue(self.kt_handle_http.set('a', 'xxxx', db=DB_1))
        self.assertTrue(self.kt_handle_http.set_bulk({'b': 'yyyy', 'c': 'zzzz'}, db=DB_1))
        self.assertTrue(self.kt_handle_http.set('a1', 'xxxx', db=DB_2))
        self.assertTrue(self.kt_handle_http.set_bulk({'b1': 'yyyy', 'c1': 'zzzz'}, db=DB_2))

        d = self.kt_handle_http.get_bulk(['a', 'b', 'c'], db=DB_1)
        self.assertEqual(len(d), 3)
        self.assertEqual(d['a'], 'xxxx')
        self.assertEqual(d['b'], 'yyyy')
        self.assertEqual(d['c'], 'zzzz')
        d = self.kt_handle_http.get_bulk(['a', 'b', 'c'], db=DB_2)
        self.assertEqual(len(d), 0)

        d = self.kt_handle_http.get_bulk(['a1', 'b1', 'c1'], db=DB_2)
        self.assertEqual(len(d), 3)
        self.assertEqual(d['a1'], 'xxxx')
        self.assertEqual(d['b1'], 'yyyy')
        self.assertEqual(d['c1'], 'zzzz')
        d = self.kt_handle_http.get_bulk(['a1', 'b1', 'c1'], db=DB_1)
        self.assertEqual(len(d), 0)

    def test_add(self):
        self.assertTrue(self.clear_all())

        # Should not conflict due to different databases.
        self.assertTrue(self.kt_handle_http.add('key1', 'val1', db=DB_1))
        self.assertTrue(self.kt_handle_http.add('key1', 'val1', db=DB_2))

        # Now they should.
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.add, 'key1', 'val1', db=DB_1)
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.add, 'key1', 'val1', db=DB_2)
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.add, 'key1', 'val1', db=DB_INVALID)

    def test_check(self):
        self.assertTrue(self.kt_handle_http.set('check1', 'abc', db=DB_2))
        self.assertTrue(self.kt_handle_http.check('check1', db=DB_2))
        self.assertFalse(self.kt_handle_http.check('check1', db=DB_1))

    def test_seize(self):
        self.assertTrue(self.kt_handle_http.set('seize1', 'abc', db=DB_2))
        self.assertEqual(self.kt_handle_http.get('seize1', db=DB_2), 'abc')
        self.assertEqual(self.kt_handle_http.get('seize1', db=DB_1), None)
        self.assertEqual(self.kt_handle_http.seize('seize1', db=DB_2), 'abc')
        self.assertEqual(self.kt_handle_http.get('seize1', db=DB_2), None)

    def test_replace(self):
        self.assertTrue(self.clear_all())
        self.assertTrue(self.kt_handle_http.add('key1', 'val1', db=DB_1))
        self.assertFalse(self.kt_handle_http.replace('key1', 'val2', db=DB_2))
        self.assertTrue(self.kt_handle_http.replace('key1', 'val2', db=DB_1))
        self.assertFalse(self.kt_handle_http.replace('key1', 'val2', db=DB_INVALID))

        self.assertTrue(self.kt_handle_http.add('key2', 'aaa'))
        self.assertTrue(self.kt_handle_http.replace('key2', 'bbb'))
        self.assertTrue(self.kt_handle_http.replace('key1', 'zzz'))
        self.assertEqual(self.kt_handle_http.get('key2'), 'bbb')
        self.assertEqual(self.kt_handle_http.get('key1'), 'zzz')

    def test_cas(self):
        self.assertTrue(self.clear_all())
        self.assertTrue(self.kt_handle_http.set('key', 'xxx'))
        self.assertEqual(self.kt_handle_http.get('key', db=DB_2), None)
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.cas, 'key', old_val='xxx', new_val='yyy', db=DB_2)
        self.assertEqual(self.kt_handle_http.get('key', db=DB_1), 'xxx')
        self.assertTrue(self.kt_handle_http.cas('key', old_val='xxx', new_val='yyy', db=DB_1))
        self.assertTrue(self.kt_handle_http.cas('key', new_val='xxx', db=DB_2))

    def test_remove(self):
        self.assertTrue(self.clear_all())
        self.assertTrue(self.kt_handle_http.add('key', 'value', db=DB_1))
        self.assertTrue(self.kt_handle_http.add('key', 'value', db=DB_2))

        self.assertTrue(self.kt_handle_http.remove('key', db=DB_1))
        self.assertEqual(self.kt_handle_http.get('key', db=DB_2), 'value')
        assert self.kt_handle_http.get('key', db=DB_1) is None

    def test_vacuum(self):
        self.assertTrue(self.kt_handle_http.vacuum())
        self.assertTrue(self.kt_handle_http.vacuum(db=DB_1))
        self.assertTrue(self.kt_handle_http.vacuum(db=DB_2))
        self.assertRaises(KyotoTycoonException, self.kt_handle_http.vacuum, db=DB_INVALID)

    def test_append(self):
        self.assertTrue(self.clear_all())
        self.assertTrue(self.kt_handle_http.set('key', 'xxx', db=DB_1))
        self.assertTrue(self.kt_handle_http.set('key', 'xxx', db=DB_2))
        self.assertTrue(self.kt_handle_http.append('key', 'xxx', db=DB_1))

        self.assertEqual(self.kt_handle_http.get('key', db=DB_1), 'xxxxxx')
        self.assertEqual(self.kt_handle_http.get('key', db=DB_2), 'xxx')

    def test_increment(self):
        self.assertTrue(self.clear_all())
        self.assertEqual(self.kt_handle_http.increment('key', 0, db=DB_1), 0)
        self.assertEqual(self.kt_handle_http.increment('key', 0, db=DB_2), 0)

        self.assertEqual(self.kt_handle_http.increment('key', 100, db=DB_1), 100)
        self.assertEqual(self.kt_handle_http.increment('key', 200, db=DB_2), 200)
        self.assertEqual(self.kt_handle_http.increment('key', 100, db=DB_1), 200)
        self.assertEqual(self.kt_handle_http.increment('key', 200, db=DB_2), 400)
        self.assertEqual(self.kt_handle_http.get_int('key', db=DB_1), 200)
        self.assertEqual(self.kt_handle_http.get_int('key', db=DB_2), 400)

    def test_match_prefix(self):
        self.assertTrue(self.clear_all())
        self.assertTrue(self.kt_handle_http.set('abcdef', 'val', db=DB_1))
        self.assertTrue(self.kt_handle_http.set('fedcba', 'val', db=DB_2))

        list = self.kt_handle_http.match_prefix('abc', db=DB_1)
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 'abcdef')
        list = self.kt_handle_http.match_prefix('abc', db=DB_2)
        self.assertEqual(len(list), 0)
        list = self.kt_handle_http.match_prefix('fed', db=DB_1)
        self.assertEqual(len(list), 0)
        list = self.kt_handle_http.match_prefix('fed', db=DB_2)
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 'fedcba')

    def test_set_get_bin(self):
        self.assertTrue(self.clear_all())
        self.assertTrue(self.kt_handle_bin.set('ice', 'cream', db=DB_2))
        self.assertFalse(self.kt_handle_bin.set('palo', 'alto', db=DB_INVALID))

        self.assertEqual(self.kt_handle_bin.get('ice'), None)
        self.assertEqual(self.kt_handle_bin.get('ice', db=DB_1), None)
        self.assertFalse(self.kt_handle_bin.get('ice', db=DB_INVALID))

        self.assertEqual(self.kt_handle_bin.get('ice', db=DB_2), 'cream')
        self.assertEqual(self.kt_handle_http.count(db=DB_1), 0)
        self.assertEqual(self.kt_handle_http.count(db=DB_2), 1)

        self.assertTrue(self.kt_handle_bin.set('frozen', 'yoghurt', db=DB_1))
        self.assertEqual(self.kt_handle_http.count(db=DB_1), 1)

        self.assertEqual(self.kt_handle_bin.get('frozen'), 'yoghurt')
        self.assertEqual(self.kt_handle_bin.get('frozen', db=DB_1), 'yoghurt')
        self.assertEqual(self.kt_handle_bin.get('frozen', db=DB_2), None)
        self.assertFalse(self.kt_handle_bin.get('frozen', db=DB_INVALID), None)

        self.assertTrue(self.kt_handle_http.clear(db=DB_1))
        self.assertEqual(self.kt_handle_http.count(db=DB_1), 0)
        self.assertEqual(self.kt_handle_http.count(db=DB_2), 1)

    def test_get_multi_bin(self):
        self.assertTrue(self.clear_all())

        self.assertTrue(self.kt_handle_bin.set('a', 'xxxx', db=DB_1))
        self.assertTrue(self.kt_handle_bin.set_bulk({'b': 'yyyy', 'c': 'zzzz'}, db=DB_1))
        self.assertTrue(self.kt_handle_bin.set('a1', 'xxxx', db=DB_2))
        self.assertTrue(self.kt_handle_bin.set_bulk({'b1': 'yyyy', 'c1': 'zzzz'}, db=DB_2))

        d = self.kt_handle_bin.get_bulk(['a', 'b', 'c'], db=DB_1, atomic=False)
        self.assertEqual(len(d), 3)
        self.assertEqual(d['a'], 'xxxx')
        self.assertEqual(d['b'], 'yyyy')
        self.assertEqual(d['c'], 'zzzz')
        d = self.kt_handle_bin.get_bulk(['a', 'b', 'c'], db=DB_2, atomic=False)
        self.assertEqual(len(d), 0)

        d = self.kt_handle_bin.get_bulk(['a1', 'b1', 'c1'], db=DB_2, atomic=False)
        self.assertEqual(len(d), 3)
        self.assertEqual(d['a1'], 'xxxx')
        self.assertEqual(d['b1'], 'yyyy')
        self.assertEqual(d['c1'], 'zzzz')
        d = self.kt_handle_bin.get_bulk(['a1', 'b1', 'c1'], db=DB_1, atomic=False)
        self.assertEqual(len(d), 0)

    def test_remove_bin(self):
        self.assertTrue(self.clear_all())
        self.assertTrue(self.kt_handle_bin.set('key', 'value', db=DB_1))
        self.assertTrue(self.kt_handle_bin.set('key', 'value', db=DB_2))

        self.assertTrue(self.kt_handle_bin.remove('key', db=DB_1))
        self.assertEqual(self.kt_handle_bin.get('key', db=DB_2), 'value')
        assert self.kt_handle_bin.get('key', db=DB_1) is None

if __name__ == '__main__':
    unittest.main()
