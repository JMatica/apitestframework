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

# library imports
import pytest
import responses

# local imports
from apitestframework.core.api_test import ApiTest
from apitestframework.utils.test_status import TestStatus

class TestApiTest(object):
    '''
    Test core.api_test module
    '''

    @responses.activate
    def test_01(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396',
            'verify_ssl': False
        }, {
            'name': 'test_01',
            'expected': 'config/output/goeuro-status-expected.json'
        })
        responses.add(responses.GET, 'http://localhost:9396',
                  json={'version': '0.3.1', 'status': 'OK'}, status=200)
        assert at.status == TestStatus.PENDING
        assert at.enabled == True
        assert at.name == 'test_01'
        assert at._verify_ssl == False
        status, data = at.run()
        assert status == TestStatus.SUCCESS
        assert data['version'] == '0.3.1'
        assert data['status'] == 'OK'

    @responses.activate
    def test_02(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json'
        })
        responses.add(responses.GET, 'http://localhost:9396',
                  json={'version': '0.3.1', 'status': 'OK'}, status=302)
        status, data = at.run()
        assert status == TestStatus.FAILURE
        assert data == {'version': '0.3.1', 'status': 'OK'}

    @responses.activate
    def test_03(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json'
        })
        responses.add(responses.GET, 'http://localhost:9396',
                  json=None, status=200)
        status, data = at.run()
        assert status == TestStatus.FAILURE
        assert data == ''

    @responses.activate
    def test_04(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json'
        })
        responses.add(responses.GET, 'http://localhost:9396',
                  json={'some': 'value'}, status=200)
        status, data = at.run()
        assert status == TestStatus.FAILURE
        assert data == {'some': 'value'}

    def test_05(self):
        with pytest.raises(ValueError) as pytest_wrapped_e:
            ApiTest({}, {
                'expected': 'config/output/goeuro-status-expected.json'
            })
        assert pytest_wrapped_e.type == ValueError
        assert 'missing url' in str(pytest_wrapped_e.value).lower()

    def test_06(self):
        with pytest.raises(ValueError) as pytest_wrapped_e:
            ApiTest({
                'base_url': 'http://localhost:9396'
            }, {})
        assert pytest_wrapped_e.type == ValueError
        assert 'missing expected result file' in str(pytest_wrapped_e.value).lower()

    def test_07(self):
        with pytest.raises(FileNotFoundError) as pytest_wrapped_e:
            ApiTest({
                'base_url': 'http://localhost:9396'
            }, {
                'expected': 'expected.json'
            })
        assert pytest_wrapped_e.type == FileNotFoundError
        assert 'could not find expected result file' in str(pytest_wrapped_e.value).lower()

    @responses.activate
    def test_08(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json',
            'extract': [{
                'name': 'extvrs',
                'key': 'version'
            }]
        })
        responses.add(responses.GET, 'http://localhost:9396',
                  json={'version': '0.3.1', 'status': 'OK'}, status=200)
        at.run()
        ext = at.extract_values()
        assert len(ext.keys()) == 1
        assert ext['extvrs'] == '0.3.1'

    def test_09(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json',
            'inject': [{
                'name': 'field',
                'type': 'path'
            }]
        })
        at.inject_values({
            'field': 'added_path'
        })
        assert at._url == 'http://localhost:9396/added_path'

    def test_09_bis(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396/'
        }, {
            'expected': 'config/output/goeuro-status-expected.json',
            'inject': [{
                'name': 'field',
                'type': 'path'
            }]
        })
        at.inject_values({
            'field': 'added_path'
        })
        assert at._url == 'http://localhost:9396/added_path'

    def test_10(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json',
            'payload': {
                'id': 'noid'
            },
            'inject': [{
                'name': 'field',
                'type': 'body',
                'key': 'id'
            }]
        })
        assert at._payload['id'] == 'noid'
        at.inject_values({
            'field': 'added_body'
        })
        assert at._payload['id'] == 'added_body'

    def test_11(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json',
            'inject': [{
                'name': 'field',
                'type': 'query',
                'key': 'id'
            }]
        })
        assert at._params is None
        at.inject_values({
            'field': 'added_query'
        })
        assert at._params == { 'id': 'added_query' }

    def test_12(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json',
            'inject': [{
                'name': 'field',
                'type': 'header',
                'key': 'id'
            }]
        })
        assert at._headers == []
        at.inject_values({
            'field': 'added_header'
        })
        assert at._headers[0].key == 'id'
        assert at._headers[0].value == 'added_header'

    def test_13(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json',
            'headers': {
                'id': {
                    'value': 'header'
                }
            },
            'inject': [{
                'name': 'field',
                'type': 'header',
                'key': 'id'
            }]
        })
        assert at._headers[0].key == 'id'
        assert at._headers[0].value == 'header'
        at.inject_values({
            'field': 'added_header'
        })
        assert at._headers[0].key == 'id'
        assert at._headers[0].value == 'added_header'

    def test_14(self):
        at = ApiTest({
            'base_url': 'http://localhost:9396'
        }, {
            'expected': 'config/output/goeuro-status-expected.json',
            'headers': {
                'id': {
                    'value': 'header',
                    'hide': True
                },
                'some': {
                    'value': 'thing'
                }
            }
        })
        assert len(at._get_headers()) == 1
