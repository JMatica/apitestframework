#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018 JMatica Srl
#
# This file is part of apitestframework.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# system imports
import os

# library imports
import pytest

# local imports
from apitestframework.utils.config import get_conf_value, load_config

class TestConfig(object):
    '''
    Test utils.config module
    '''

    def test_missing_load_config(self):
        '''
        Test load_config method on error
        '''
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            load_config('nono.json')
        assert pytest_wrapped_e.type == SystemExit
        assert 'missing configuration file' in pytest_wrapped_e.value.code.lower()

    def test_load_config(self):
        '''
        Test load_config method
        '''
        with open('tmp.json', 'w', encoding='utf-8') as f:
            f.write('{"key":"value"}')
        conf = load_config('tmp.json')
        assert conf['key'] == 'value'
        os.remove('tmp.json')

    def test_get_conf_value(self):
        '''
        Test get_conf_value method
        '''
        data = {
            'key': 42
        }
        def_val = ''
        assert get_conf_value(data, 'key') == 42
        assert get_conf_value(data, 'nokey') is None
        assert get_conf_value(data, 'nokey', def_val) == def_val
        assert get_conf_value(None, 'key') is None
        assert get_conf_value(None, 'key', def_val) == def_val
        assert get_conf_value(None, None) is None
        assert get_conf_value(None, None, def_val) == def_val
