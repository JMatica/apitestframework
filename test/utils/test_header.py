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

# local imports
from apitestframework.utils.header import Header
from apitestframework.utils.header_utils import get_headers_list, merge_headers_lists

class TestHeader(object):
    '''
    Test utils.header module
    '''

    def test_header(self):
        '''
        Test header
        '''
        # content-type
        h0 = Header('Content-Type', {
            'value': 'application/json'
        })
        assert h0.hide == False
        assert h0._placeholder == '{}'
        assert h0.key == 'Content-Type'
        assert h0.value == 'application/json'
        # authorization
        os.environ['CUSTOM_TOKEN'] = 'pippo'
        h1 = Header('Authorization', {
            'value': 'Basic %',
            'placeholder': '%',
            'envName': 'CUSTOM_TOKEN'
        })
        assert h1.hide == False
        assert h1._placeholder == '%'
        assert h1.key == 'Authorization'
        assert h1._orig_value == 'Basic %'
        assert h1.value == 'Basic pippo'
        del os.environ['CUSTOM_TOKEN']
        # custom
        h2 = Header('CustomHeader', {
            'value': 'Hello {}',
            'hide': True,
            'envName': 'ENV_VAR_NOT_PRESENT'
        })
        assert h2.hide == True
        assert h2._placeholder == '{}'
        assert h2.key == 'CustomHeader'
        assert h2.value == 'Hello {}'
        assert h2.value == h2._orig_value
        h2.value = 'World'
        assert h2.value == 'Hello World'
        # custom 2
        h3 = Header('CustomHeader', {
            'value': 'Hello'
        })
        assert h3.hide == False
        assert h3._placeholder == '{}'
        assert h3.key == 'CustomHeader'
        assert h3.value == 'Hello'
        h3.value = 'Goodbye'
        assert h3.value == 'Goodbye'
