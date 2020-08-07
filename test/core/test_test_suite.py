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
import responses

# local imports
from apitestframework.core.test_suite import TestSuite
from apitestframework.utils.test_status import TestStatus

class TestTestSuite(object):
    '''
    Test core.test_suite module
    '''

    def test_01(self):
        ts = TestSuite({
            'name': 'test test suite',
            'baseUrl': 'http://localhost:9093'
        })
        assert ts.name == 'test test suite'
        assert len(ts._tests) == 0

    def test_02(self):
        with pytest.raises(ValueError) as pytest_wrapped_e:
            TestSuite({
            'name': 'test test suite'
        })
        assert pytest_wrapped_e.type == ValueError
        assert 'non-valid baseurl' in str(pytest_wrapped_e.value).lower()

    def test_03(self):
        os.environ['TEST_BASE_URL'] = 'http://127.0.0.1:8888'
        ts = TestSuite({
            'name': 'test test suite',
            'baseUrl': 'http://localhost:9093',
            'envOverride': [
                {
                    'name': 'baseUrl',
                    'envName': 'TEST_BASE_URL'
                }
            ]
        })
        assert ts._base_url == 'http://127.0.0.1:8888'
        del os.environ['TEST_BASE_URL']

    def test_04(self):
        ts = TestSuite({
            'name': 'test test suite',
            'baseUrl': 'http://localhost:9093',
            'tests': [
                {
                    'name': 'Status',
                    'path': '/v1/status',
                    'expected': 'config/output/goeuro-status-expected.json'
                }
            ]
        })
        assert len(ts._tests) == 1

    @responses.activate
    def test_05(self):
        ts = TestSuite({
            'name': 'test test suite',
            'baseUrl': 'http://localhost:9093',
            'tests': [
                {
                    'name': 'Status',
                    'path': '/v1/status',
                    'expected': 'config/output/goeuro-status-expected.json'
                }
            ]
        })
        responses.add(responses.GET, 'http://localhost:9093/v1/status',
                  json={'version': '0.3.1', 'status': 'OK'}, status=200)
        ts.run()
        assert len(ts.test_results) == 1
        assert ts.test_results[0] == ('Status', TestStatus.SUCCESS, {'version': '0.3.1', 'status': 'OK'})

    @responses.activate
    def test_06(self):
        ts = TestSuite({
            'name': 'test test suite',
            'baseUrl': 'http://localhost:9093',
            'tests': [
                {
                    'name': 'Status',
                    'path': '/v1/status',
                    'expected': 'config/output/goeuro-status-expected.json',
                    'enabled': False
                }
            ]
        })
        responses.add(responses.GET, 'http://localhost:9093/v1/status',
                  json={'version': '0.3.1', 'status': 'OK'}, status=200)
        ts.run()
        assert len(ts.test_results) == 1
        assert ts.test_results[0] == ('Status', TestStatus.SKIPPED, None)

    @responses.activate
    def test_07(self):
        ts = TestSuite({
            'name': 'test test suite',
            'baseUrl': 'http://localhost:9093',
            'tests': [
                {
                    'name': 'Status',
                    'path': '/v1/status',
                    'expected': 'config/output/goeuro-status-expected.json',
                    'extract': [
                        {
                            'name': 'version',
                            'key': 'version'
                        }
                    ]
                },
                {
                    'name': 'StatusNext',
                    'path': '/v1/status',
                    'expected': 'config/output/goeuro-status-expected.json',
                    'inject': [
                        {
                            'name': 'version',
                            'type': 'header',
                            'key': 'injected_header'
                        }
                    ]
                }
            ]
        })
        responses.add(responses.GET, 'http://localhost:9093/v1/status',
                  json={'version': '0.3.1', 'status': 'OK'}, status=200)
        ts.run()
        assert len(ts.test_results) == 2
        assert ts.test_results[0] == ('Status', TestStatus.SUCCESS, {'version': '0.3.1', 'status': 'OK'})
        assert ts.test_results[1] == ('StatusNext', TestStatus.SUCCESS, {'version': '0.3.1', 'status': 'OK'})
        assert len(ts._tests[1]._headers) == 1
        assert ts._tests[1]._headers[0].key == 'injected_header'
        assert ts._tests[1]._headers[0].value == '0.3.1'

    @responses.activate
    def test_08(self):
        ts = TestSuite({
            'name': 'test test suite',
            'baseUrl': 'http://localhost:9093',
            'tests': [
                {
                    'name': 'Status',
                    'path': '/v1/status',
                    'expected': 'config/output/goeuro-status-expected.json'
                },
                {
                    'name': 'StatusNext',
                    'path': '/v1/statusnext',
                    'expected': 'config/output/goeuro-status-expected.json'
                }
            ]
        })
        responses.add(responses.GET, 'http://localhost:9093/v1/status',
                  json={'version': '0.3.1', 'status': 'OK'}, status=302)
        ts.run()
        assert len(ts.test_results) == 1
        assert ts.test_results[0] == ('Status', TestStatus.FAILURE, {'version': '0.3.1', 'status': 'OK'})
