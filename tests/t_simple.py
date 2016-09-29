#!/usr/bin/env python
#
# Copyright 2011, Toru Maesaka
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.

import config
import unittest
from kyototycoon import KyotoTycoon, KyotoTycoonException, KT_PACKER_PICKLE

class UnitTest(unittest.TestCase):
    def setUp(self):
        self.kt_handle = KyotoTycoon(binary=False, pack_type=KT_PACKER_PICKLE)
        self.kt_handle.open(port=11978)
        self.LARGE_KEY_LEN = 8000

    def tearDown(self):
        self.kt_handle.close()

    def test_set(self):
        self.assertTrue(self.kt_handle.clear())

        self.assertTrue(self.kt_handle.set('key', 'value'))

        self.assertTrue(self.kt_handle.set('k e y', 'v a l u e'))
        self.assertTrue(self.kt_handle.set('k\te\ty', 'tabbed'))

        self.assertEqual(self.kt_handle.get('key'), 'value')
        self.assertEqual(self.kt_handle.get('k e y'), 'v a l u e')
        self.assertEqual(self.kt_handle.get('k\te\ty'), 'tabbed')

        self.assertTrue(self.kt_handle.set('\\key', '\\xxx'))
        self.assertEqual(self.kt_handle.get('\\key'), '\\xxx')
        self.assertEqual(self.kt_handle.count(), 4)

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

    def test_cas(self):
        self.assertTrue(self.kt_handle.clear())

        self.assertTrue(self.kt_handle.set('key', 'xxx'))
        self.assertTrue(self.kt_handle.cas('key', old_val='xxx', new_val='yyy'))
        self.assertEqual(self.kt_handle.get('key'), 'yyy')

        self.assertTrue(self.kt_handle.cas('key', old_val='yyy'))
        assert self.kt_handle.get('key') is None
        self.assertTrue(self.kt_handle.cas('key', new_val='zzz'))
        self.assertEqual(self.kt_handle.get('key'), 'zzz')

        self.assertRaises(KyotoTycoonException, self.kt_handle.cas, 'key', old_val='foo', new_val='zz')
        self.assertEqual(self.kt_handle.get('key'), 'zzz')

    def test_remove(self):
        self.assertTrue(self.kt_handle.clear())

        self.assertFalse(self.kt_handle.remove('must fail key'))
        self.assertTrue(self.kt_handle.set('deleteable key', 'xxx'))
        self.assertTrue(self.kt_handle.remove('deleteable key'))

    def test_replace(self):
        self.assertTrue(self.kt_handle.clear())

        # Must Fail - Can't replace something that doesn't exist.
        self.assertFalse(self.kt_handle.replace('xxxxxx', 'some value'))

        # Popuate then Replace.
        self.assertTrue(self.kt_handle.set('apple', 'ringo'))
        self.assertTrue(self.kt_handle.replace('apple', 'apfel'))
        self.assertEqual(self.kt_handle.get('apple'), 'apfel')

        self.assertTrue(self.kt_handle.replace('apple', 212))
        self.assertEqual(self.kt_handle.get('apple'), 212)
        self.assertTrue(self.kt_handle.replace('apple', 121))
        self.assertEqual(self.kt_handle.get('apple'), 121)

    def test_append(self):
        self.assertTrue(self.kt_handle.clear())
        self.assertTrue(self.kt_handle.set('k1', 'abc'))
        self.assertTrue(self.kt_handle.append('k1', 'def'))
        self.assertEqual(self.kt_handle.get('k1'), 'abcdef')

        self.assertTrue(self.kt_handle.append('k2', 'new val'))
        self.assertEqual(self.kt_handle.get('k2'), 'new val')

        self.assertTrue(self.kt_handle.set('k3', 777))

        self.assertTrue(self.kt_handle.set('k4', b'abc'))
        self.assertTrue(self.kt_handle.append('k4', 'abc'))
        self.assertEqual(self.kt_handle.get('k4'), b'abcabc')

        self.assertTrue(self.kt_handle.set('k5', 'abc'))
        self.assertTrue(self.kt_handle.append('k5', b'abc'))
        self.assertEqual(self.kt_handle.get('k5'), 'abcabc')

    def test_add(self):
        self.assertTrue(self.kt_handle.clear())
        self.assertTrue(self.kt_handle.set('stewie', 'griffin'))

        # Must Fail - Stewie exists
        self.assertRaises(KyotoTycoonException, self.kt_handle.add, 'stewie', 'hopkin')

        # New records
        self.assertTrue(self.kt_handle.add('peter', 'griffin'))
        self.assertTrue(self.kt_handle.add('lois', 'griffin'))
        self.assertTrue(self.kt_handle.add('seth', 'green'))
        self.assertTrue(self.kt_handle.add('nyc', 'new york city'))

        self.assertTrue(self.kt_handle.add('number', 111))
        self.assertEqual(self.kt_handle.get('number'), 111)

    def test_check(self):
        self.assertTrue(self.kt_handle.set('check1', 'abc'))
        self.assertTrue(self.kt_handle.check('check1'))

        self.assertTrue(self.kt_handle.remove('check1'))
        self.assertFalse(self.kt_handle.check('check1'))

    def test_seize(self):
        self.assertTrue(self.kt_handle.set('seize1', 'abc'))
        self.assertEqual(self.kt_handle.get('seize1'), 'abc')
        self.assertEqual(self.kt_handle.seize('seize1'), 'abc')
        self.assertEqual(self.kt_handle.get('seize1'), None)
        self.assertEqual(self.kt_handle.seize('seize2'), None)

    def test_set_bulk(self):
        self.assertTrue(self.kt_handle.clear())

        dict = {
            'k1': 'one',
            'k2': 'two',
            'k3': 'three',
            'k4': 'four',
            'k\n5': 'five',
            'k\t6': 'six',
            'k7': 111
        }

        n = self.kt_handle.set_bulk(dict)
        self.assertEqual(len(dict), n)
        self.assertEqual(self.kt_handle.get('k1'), 'one')
        self.assertEqual(self.kt_handle.get('k2'), 'two')
        self.assertEqual(self.kt_handle.get('k3'), 'three')
        self.assertEqual(self.kt_handle.get('k4'), 'four')
        self.assertEqual(self.kt_handle.get('k\n5'), 'five')
        self.assertEqual(self.kt_handle.get('k\t6'), 'six')
        self.assertEqual(self.kt_handle.get('k7'), 111)

        d = self.kt_handle.get_bulk(['k1', 'k2', 'k3', 'k4',
                                     'k\n5', 'k\t6', 'k7'])

        self.assertEqual(len(d), len(dict))
        self.assertEqual(d, dict)

        self.assertEqual(self.kt_handle.count(), 7)
        n = self.kt_handle.remove_bulk(['k1', 'k2', 'k\t6'])
        self.assertEqual(self.kt_handle.count(), 4)
        n = self.kt_handle.remove_bulk(['k3'], atomic=True)
        self.assertEqual(self.kt_handle.count(), 3)

    def test_get_bulk(self):
        self.assertTrue(self.kt_handle.clear())
        self.assertTrue(self.kt_handle.set('a', 'one'))
        self.assertTrue(self.kt_handle.set('b', 'two'))
        self.assertTrue(self.kt_handle.set('c', 'three'))
        self.assertTrue(self.kt_handle.set('d', 'four'))

        d = self.kt_handle.get_bulk(['a','b','c','d'])
        assert d is not None

        self.assertEqual(d['a'], 'one')
        self.assertEqual(d['b'], 'two')
        self.assertEqual(d['c'], 'three')
        self.assertEqual(d['d'], 'four')
        self.assertEqual(len(d), 4)

        d = self.kt_handle.get_bulk(['a','x','y','d'])
        self.assertEqual(len(d), 2)
        d = self.kt_handle.get_bulk(['w','x','y','z'])
        self.assertEqual(len(d), 0)
        d = self.kt_handle.get_bulk([])
        self.assertEqual(d, {})

    def test_large_key(self):
        large_key = 'x' * self.LARGE_KEY_LEN
        self.assertTrue(self.kt_handle.set(large_key, 'value'))
        self.assertEqual(self.kt_handle.get(large_key), 'value')

    def test_report(self):
        report = None
        report = self.kt_handle.report()
        assert report is not None

        self.assertTrue(int(report['serv_conn_count']) > 0)

    def test_status(self):
        self.assertTrue(self.kt_handle.clear())
        status = None
        status = self.kt_handle.status()
        assert status is not None

        self.assertTrue(status['count'], 0)
        self.kt_handle.set('red', 'apple')
        self.kt_handle.set('yellow', 'banana')
        self.kt_handle.set('pink', 'peach')
        self.assertTrue(status['count'], 3)

    def test_vacuum(self):
        self.assertTrue(self.kt_handle.vacuum())

    def test_match_prefix(self):
        self.assertTrue(self.kt_handle.clear())
        self.assertTrue(self.kt_handle.set('abc', 'val'))
        self.assertTrue(self.kt_handle.set('abcd', 'val'))
        self.assertTrue(self.kt_handle.set('abcde', 'val'))
        self.assertTrue(self.kt_handle.set('abcdef', 'val'))
        self.assertTrue(self.kt_handle.set('abcdefg', 'val'))
        self.assertTrue(self.kt_handle.set('abcdefgh', 'val'))

        list = self.kt_handle.match_prefix('abc')
        self.assertEqual(len(list), 6)
        list = self.kt_handle.match_prefix('abcd')
        self.assertEqual(len(list), 5)
        list = self.kt_handle.match_prefix('abc', 1)
        self.assertEqual(list[0][:3], 'abc')
        list = self.kt_handle.match_prefix('abc', 3)
        self.assertEqual(len(list), 3)

    def test_match_regex(self):
        self.assertTrue(self.kt_handle.clear())
        self.assertTrue(self.kt_handle.set('abc', 'val'))
        self.assertTrue(self.kt_handle.set('abcd', 'val'))
        self.assertTrue(self.kt_handle.set('abcde', 'val'))

        list = self.kt_handle.match_regex('^abc')
        self.assertEqual(len(list), 3)
        list = self.kt_handle.match_regex('^abcd')
        self.assertEqual(len(list), 2)
        list = self.kt_handle.match_regex('e$')
        self.assertEqual(len(list), 1)
        list = self.kt_handle.match_regex('^abc', 2)
        self.assertEqual(len(list), 2)

    def test_match_similar(self):
        self.assertTrue(self.kt_handle.clear())
        self.assertTrue(self.kt_handle.set('potatoes', 'val'))
        self.assertTrue(self.kt_handle.set('potataes', 'val'))
        self.assertTrue(self.kt_handle.set('patataes', 'val'))

        list = self.kt_handle.match_similar('potatoes', 0)
        self.assertEqual(len(list), 1)
        list = self.kt_handle.match_similar('potatoes', 1)
        self.assertEqual(len(list), 2)
        list = self.kt_handle.match_similar('potatoes', 2)
        self.assertEqual(len(list), 3)
        list = self.kt_handle.match_similar('potatoes', 2, 1)
        self.assertEqual(len(list), 1)

        self.assertTrue(self.kt_handle.set('cafe', 'val'))
        self.assertTrue(self.kt_handle.set(b'caf\xc3'.decode('iso8859-1'), 'val'))
        list = self.kt_handle.match_similar('cafe', 1)
        self.assertEqual(len(list), 2)


    def test_cursor(self):
        self.assertTrue(self.kt_handle.clear())
        self.assertEqual(self.kt_handle.count(), 0)
        self.assertTrue(self.kt_handle.set('abc', 'val'))
        self.assertTrue(self.kt_handle.set('abcd', 'val'))
        self.assertTrue(self.kt_handle.set('abcde', 'val'))
        self.assertEqual(self.kt_handle.count(), 3)

        cur = self.kt_handle.cursor()
        self.assertTrue(cur.jump())
        while True:
            self.assertEqual(cur.get_key()[:3], 'abc')
            self.assertEqual(cur.get_value(), 'val')

            pair = cur.get()
            self.assertEqual(len(pair), 2)
            self.assertEqual(pair[0][:3], 'abc')
            self.assertEqual(pair[1], 'val')

            self.assertTrue(cur.set_value('foo'))
            self.assertEqual(cur.get_value(), 'foo')

            if pair[0] == 'abcd':
                self.assertTrue(cur.remove())
                break

            if not cur.step():
                break

        self.assertTrue(cur.delete())
        self.assertEqual(self.kt_handle.count(), 2)

        self.assertTrue(self.kt_handle.set('zabc', 'val'))
        self.assertTrue(self.kt_handle.set('zabcd', 'val'))
        self.assertTrue(self.kt_handle.set('zabcde', 'val'))
        self.assertEqual(self.kt_handle.count(), 5)

        cur = self.kt_handle.cursor()
        self.assertTrue(cur.jump(key='zabc'))
        while True:
            pair = cur.get()

            if pair[0] == 'zabc':
                dict = cur.seize()
                self.assertEqual(len(dict), 2)
                self.assertEqual(dict['key'][:4], 'zabc')
                self.assertEqual(dict['value'], 'val')

            if not cur.step():
                break

        self.assertTrue(cur.delete())
        self.assertEqual(self.kt_handle.count(), 4)


if __name__ == '__main__':
    unittest.main()
