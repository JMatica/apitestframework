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
import responses

# local imports
from apitestframework.core.test_run import TestRun

class TestTestRun(object):
    '''
    Test core.test_run module
    '''

    @responses.activate
    def test_01(self):
        tr = TestRun({
            'suites': [
                {
                    'name': 'MY_SUITE',
                    'baseUrl': 'http://localhost:9093',
                    'tests': [
                        {
                            'name': 'Status',
                            'path': '/v1/status',
                            'expected': 'config/output/goeuro-status-expected.json'
                        }
                    ]
                }
            ]
        })
        responses.add(responses.GET, 'http://localhost:9093/v1/status',
                  json={'version': '0.3.1', 'status': 'OK'}, status=200)
        try:
            tr.run()
        except SystemExit as e:
            assert False
        else:
            assert True

    @responses.activate
    def test_02(self):
        tr = TestRun({
            'suites': [
                {
                    'name': 'MY_SUITE',
                    'baseUrl': 'http://localhost:9093',
                    'tests': [
                        {
                            'name': 'Status',
                            'path': '/v1/status',
                            'expected': 'config/output/goeuro-status-expected.json'
                        }
                    ]
                }
            ]
        })
        responses.add(responses.GET, 'http://localhost:9093/v1/status',
                  json={'version': '0.3.1', 'status': 'OK'}, status=302)
        try:
            tr.run()
        except SystemExit as e:
            assert True
        else:
            assert False
