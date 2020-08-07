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

# local imports
from apitestframework.utils.api_test_utils import check_result_code, check_result_content

class TestApiTestUtils(object):
    '''
    Test utils.api_test_utils module
    '''

    def test_check_result_code(self):
        '''
        Test check_result_code method
        '''
        assert check_result_code(500, 200) == False
        assert check_result_code(200, 200) == True

    def test_check_result_content_01(self):
        '''
        Test check_result_content method
        '''
        expected = {
            'id': 'some_id',
            'solutions': [
                {
                    'solutionId': 'VCC-2001-09400-59700-1567116000'
                }
            ],
            'money': {
                'currency': 'EUR'
            }
        }
        result = {
            'id': 'some_id',
            'solutions': [
                {
                    'solutionId': 'VCC-2001-09400-59700-1567116000'
                }
            ],
            'money': {
                'currency': 'EUR'
            }
        }
        assert check_result_content(result, expected) == True

    def test_check_result_content_02(self):
        '''
        Test check_result_content method
        '''
        expected = {
            'id': 'some_id',
            'solutions': [
                {
                    'solutionId': 'VCC-2001-09400-59700-1567116000'
                }
            ],
            'money': {
                'currency': 'EUR'
            }
        }
        expected_2 = {
            'id': 'some_id',
            'solutions': [
                {
                    'solutionId': 'VCC-2001-09400-59700-1567116000'
                }
            ],
            'money': {
                'currency': 'EUR',
                'price': 200
            }
        }
        result = {
            'solutions': [
                {
                    'solutionId': 'VCC-2001-09400-59700-1567116000'
                }
            ],
            'money': {
                'currency': 'USD'
            }
        }
        assert check_result_content(result, expected) == False
        assert check_result_content(result, expected, None, [{ 'key': 'id', 'type': 'ignore' }, { 'key': 'money.currency', 'type': 'exist' }]) == True
        assert check_result_content(result, expected_2, None, [{ 'key': 'money.price', 'type': 'exist' }]) == False
