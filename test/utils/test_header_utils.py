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

class TestHeaderUtils(object):
    '''
    Test utils.header_utils module
    '''

    def test_get_headers_list(self):
        '''
        Test get_headers_list method
        '''
        data = {
            'headers': {
                'Content-Type': {
                    'value': 'application/json'
                },
                'Authorization': {
                    'value': 'Basic %',
                    'placeholder': '%',
                    'envName': 'CUSTOM_TOKEN'
                },
                'CustomHeader': {
                    'value': 'Ciao {}',
                    'hide': True,
                    'envName': 'ENV_VAR_NOT_PRESENT'
                }
            }
        }
        os.environ['CUSTOM_TOKEN'] = 'pippo'
        heads = get_headers_list(data)
        assert len(heads) == 3
        headsNone = get_headers_list(None)
        assert len(headsNone) == 0
        headsEmpty = get_headers_list({ 'head': {} })
        assert len(headsEmpty) == 0

    def test_merge_headers_lists(self):
        '''
        Test merge_headers_lists method
        '''
        os.environ['CUSTOM_TOKEN'] = 'pippo'
        list_a = [
            Header('Content-Type', {
                'value': 'application/json'
            }),
            # authorization
            Header('Authorization', {
                'value': 'Basic %',
                'placeholder': '%',
                'envName': 'CUSTOM_TOKEN'
            }),
            # custom
            Header('CustomHeader', {
                'value': 'Hello'
            })
        ]
        del os.environ['CUSTOM_TOKEN']
        list_b = [
            Header('CustomHeader', {
                'hide': True
            }),
            Header('Accept', {
                'value': 'application/json'
            })
        ]
        uber_list = merge_headers_lists(list_a, list_b)
        assert len(uber_list) == 4
        for h in uber_list:
            if h.key == 'CustomHeader':
                assert h.hide == True
