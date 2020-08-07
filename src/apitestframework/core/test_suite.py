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
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

# local imports
from .api_test import ApiTest
from apitestframework.utils.config import get_conf_value
from apitestframework.utils.header_utils import get_headers_list, merge_headers_lists
from apitestframework.utils.misc import camel_to_snake
from apitestframework.utils.test_status import TestStatus

logger = logging.getLogger(__name__)

class TestSuite(object):
    '''
    Collection of tests
    '''

    def __init__(self, suite_config: Dict[str, Any], global_config: Dict[str, Any] = None):
        '''
        Initialize test suite

        :param suite_config:  Configuration object for this test suite
        :type suite_config:   Dict[str, Any]
        :param global_config: Configuration object shared by all objects in the same test run
        :type global_config:  Dict[str, Any]
        '''
        self._init_conf(suite_config, global_config)
        self._tests = self._init_tests(get_conf_value(suite_config, 'tests', []), global_config)
        self._test_results = []

    # ---------------------------
    # ----- Public methods ------
    # ---------------------------

    def run(self):
        '''
        Run all the tests in the suite
        '''
        logger.info('')
        logger.info('----------------------------------------------------------------')
        logger.info('Running Test Suite: "{}"...'.format(self._name))
        logger.info('----------------------------------------------------------------')
        l = len(self._tests)
        for i, test in enumerate(self._tests):
            # run each test
            if test.enabled:
                # if enabled
                status, res = test.run()
                # save result and final status
                self._test_results.append((test.name, status, res))
                if status == TestStatus.SUCCESS:
                    # extract data from test
                    self._extracted_values.update(test.extract_values())
                    if i < l - 1 and len(self._extracted_values) > 0:
                        # inject it into next test
                        next_test = self._tests[i + 1]
                        next_test.inject_values(self._extracted_values)
                elif self._exit_on_error:
                    logger.info('Exiting on test failure. If you are sure you want to execute all tests, set `"exitOnFailure": false` in Test Suite configuration.')
                    break
            else:
                # if disabled mark as 'skipped' with no result
                self._test_results.append((test.name, TestStatus.SKIPPED, None))

    # ----------------------------
    # ----- Private methods ------
    # ----------------------------

    def _init_conf(self, suite_config: Dict[str, Any], global_config: Dict[str, Any] = None):
        '''
        Initialize configuration of the test suite

        :param suite_config:  Configuration object for this test suite
        :type suite_config:   Dict[str, Any]
        :param global_config: Configuration object shared by all objects in the same test run
        :type global_config:  Dict[str, Any]
        '''
        logger.debug('Initializing configuration')
        self._name = get_conf_value(suite_config, 'name', 'Unnamed Test Suite - {}'.format(datetime.utcnow()))
        self._exit_on_error = get_conf_value(suite_config, 'exitOnFailure', True)
        self._base_url = get_conf_value(suite_config, 'baseUrl', '')
        self._verify_ssl = get_conf_value(suite_config, 'verifySsl', True)
        # manage headers
        global_headers = get_conf_value(global_config, 'headers', [])
        suite_headers = get_headers_list(suite_config)
        self._headers = merge_headers_lists(global_headers, suite_headers)
        self._override_conf(get_conf_value(suite_config, 'envOverride', []))
        # now that we have set and overridden values, check for url validity
        if self._base_url is None or self._base_url == '':
            # TODO check for more cases.
            # We'll probably need to do it manually because urlparse awkwardly fails with 'localhost:8080' or '192.168.2.1:8080'
            raise ValueError('Non-valid baseUrl: {}'.format(self._base_url))
        self._extracted_values = {}

    def _override_conf(self, overrides: List[Dict[str, str]]):
        '''
        Override configuration parameters with values from environment variables

        :param overrides: List of fields to be replaced
        :type overrides:  List[Dict[str, str]]
        '''
        for ov in overrides:
            # retrieve value from environment
            ov_name = '_{}'.format(camel_to_snake(ov['name']))
            ov_value = os.environ.get(ov['envName'], '')
            # if we have a field to be replaced
            if hasattr(self, ov_name):
                # replace it
                logger.debug('Overriding configuration entry {} with new value {}'.format(ov['name'], ov_value))
                setattr(self, ov_name, ov_value)
            else:
                # field not found
                logger.warn('Variable {} cannot be overridden'.format(ov['name']))

    def _init_tests(self, tests_list: List[Dict[str, Any]], global_config: Dict[str, Any] = None) -> List[ApiTest]:
        '''
        Initialize the list of tests for this suite

        :param tests_list:    The list of tests in configuration
        :type tests_list:     List[Dict[str, Any]]
        :param global_config: Configuration object shared by all objects in the same test run
        :type global_config:  Dict[str, Any]

        :return: The list of tests as objects
        :rtype:  List[ApiTest]
        '''
        tests = []
        for test_data in tests_list:
            tests.append(ApiTest(self._get_shared_suite_config(), test_data))
        return tests

    def _get_shared_suite_config(self) -> Dict[str, Any]:
        '''
        Return a dictionary containing configuration entries shared by all tests in this suite

        :return: A dictionary containing configuration entries shared by all tests in this suite
        :rtype:  Dict[str, Any]
        '''
        return {
            'base_url': self._base_url,
            'verify_ssl': self._verify_ssl,
            'headers': self._headers
        }

    # -----------------------
    # ----- Properties ------
    # -----------------------

    @property
    def name(self) -> str:
        '''
        Return the test suite name

        :return: The Test Suite name
        :rtype:  str
        '''
        return self._name

    @property
    def test_results(self) -> List[Tuple[str, TestStatus, Dict[str, Any]]]:
        '''
        Return the list of test results
        Each one is a tuple (test.name, test.result, test.result_content)

        :return: The list of test results
        :rtype:  List[Tuple[str, TestStatus, Dict[str, Any]]]
        '''
        return self._test_results
