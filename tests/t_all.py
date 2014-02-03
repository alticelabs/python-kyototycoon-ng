#!/usr/bin/env python
#
# Copyright 2011, Toru Maesaka
#
# Redistribution and use of this source code is licensed under
# the BSD license. See COPYING file for license description.
#
# USAGE:
#   $ python t_all.py
#   $ python t_all.py ExpireTestCase
#   $ python t_all.py MultiTestCase
#   $ python t_all.py ScriptTestCase

import os
import re
import unittest

_TEST_MODULE_PATTERN = re.compile(r'^(t_.+)\.py$')

def _run_all_tests():
    module_names = []
    loader = unittest.TestLoader()
    test_path = os.path.join(os.path.split(__file__)[0], '.')

    for filename in os.listdir(test_path):
        match = _TEST_MODULE_PATTERN.search(filename)
        if match:
            case = match.group(1)
            if case not in ('t_expire', 't_multi', 't_script'):
                module_names.append(case)

    return loader.loadTestsFromNames(module_names)

def ExpireTestCase():
    loader = unittest.TestLoader()
    return loader.loadTestsFromName('t_expire')

def MultiTestCase():
    loader = unittest.TestLoader()
    return loader.loadTestsFromName('t_multi')

def ScriptTestCase():
    loader = unittest.TestLoader()
    return loader.loadTestsFromName('t_script')

if __name__ == '__main__':
    unittest.main(defaultTest='_run_all_tests')
