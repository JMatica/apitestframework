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
import json
import logging
import os
import requests
import traceback
import urllib3
from datetime import datetime
from typing import Any, Dict, List, Tuple

# local imports
from apitestframework.utils.api_test_utils import check_result_code, check_result_content
from apitestframework.utils.config import get_conf_value
from apitestframework.utils.header import Header
from apitestframework.utils.header_utils import get_headers_list, merge_headers_lists
from apitestframework.utils.misc import build_keys_list, get_inner_key_value, set_inner_key_value
from apitestframework.utils.test_status import TestStatus

logger = logging.getLogger(__name__)

class ApiTest(object):
    '''
    A Test against an API
    '''

    def __init__(self, shared_config: Dict[str, Any], data: Dict[str, Any]):
        '''
        Initialize the test parameters

        :param shared_config: Configuration entries shared by all tests in a suite
        :type shared_config:  Dict[str, Any]
        :param data:          The source data for this test
        :type data:           Dict[str, Any]
        '''
        self._init_from_data(shared_config, data)
        if not self._verify_ssl:
            urllib3.disable_warnings()
        self._output = None
        self._status = TestStatus.PENDING

    # ---------------------------
    # ----- Public methods ------
    # ---------------------------

    def run(self) -> Tuple[TestStatus, Dict[str, Any]]:
        '''
        Execute an API call

        :return: The test status and the call response
        :rtype:  Tuple[TestStatus, Dict[str, Any]]
        '''
        # set as running
        self._status = TestStatus.RUNNING
        headers = self._get_headers()
        # debug info
        logger.debug('~~~~~~~~~~')
        logger.info('Running Test: "{}"...'.format(self._name))
        logger.debug('URL :: {} {}'.format(self._method, self._url))
        logger.debug('params :: {}'.format(self._params))
        logger.debug('payload :: {}'.format(str(self._payload)))
        logger.debug('headers :: {}'.format(str(headers)))
        # actual call
        r = requests.request(self._method, self._url, headers=headers, json=self._payload, params=self._params, verify=self._verify_ssl)
        # parse response
        try:
            self._output = r.json()
        except json.decoder.JSONDecodeError as e:
            logger.error('Error while parsing JSON response: {}'.format(r.text))
            logger.error(str(e))
            self._status = TestStatus.FAILURE
            return self._status, r.text
        # check result and set new status
        self._status_content = check_result_content(self._output, self._expected_result, self._expected_result_file, self._response_check_exceptions)
        self._status_code = check_result_code(r.status_code, self._expected_result_code)
        if self._status_content and self._status_code:
            self._status = TestStatus.SUCCESS
        else:
            self._status = TestStatus.FAILURE
        # return result
        return self._status, self._output

    def extract_values(self) -> Dict[str, Any]:
        '''
        Extract values from APi call output

        :return: Values from APi call output
        :rtype:  Dict[str, Any]
        '''
        values = {}
        if self._output is not None:
            for k in self._extract:
                n = k['name']
                v = get_inner_key_value(self._output, k['key'])
                values[n] = v
        return values

    def inject_values(self, values: Dict[str, Any]):
        '''
        Inject given values into this test where there is a match of values "names"

        :param values: Available values to inject
        :type values:  Dict[str, Any]
        '''
        for v in self._inject:
            value_name = v['name']
            try:
                injecting_value = values[value_name]
            except KeyError:
                # values to inject not present in given values
                logger.warn('Value {} not present in given dict :: {}'.format(value_name, values))
                continue
            value_type = v['type']
            if value_type == 'body':
                # inject value into request body
                self._inject_body(v['key'], injecting_value)
            elif value_type == 'query':
                # inject value into request params
                self._inject_query(v['key'], injecting_value)
            elif value_type == 'path':
                # inject value as url path
                self._inject_path(injecting_value)
            elif value_type == 'header':
                # inject value as (part of) header value
                self._inject_header(v['key'], injecting_value)

    # ----------------------------
    # ----- Private methods ------
    # ----------------------------

    def _init_from_data(self, shared_config: Dict[str, Any], data: Dict[str, Any]):
        '''
        Initialize this test with data from a given dictionary

        :param shared_config: Configuration entries shared by all tests in a suite
        :type shared_config:  Dict[str, Any]
        :param data:          The source data
        :type data:           Dict[str, Any]
        '''
        base_url = get_conf_value(shared_config, 'base_url', '')
        verify_ssl = get_conf_value(shared_config, 'verify_ssl', True)
        # enabled: True/False
        self._enabled = get_conf_value(data, 'enabled', True)
        # name: Name of the test
        self._name = get_conf_value(data, 'name', 'Unnamed Test - {}'.format(datetime.utcnow()))
        # url: URL to call. Composed of base_url and path
        self._url = base_url + get_conf_value(data, 'path', '')
        if self._url is None or self._url == '':
            raise ValueError('[Test {}] Missing URL'.format(self._name))
        # verify_ssl: whether to validate self-signed certificates
        self._verify_ssl = verify_ssl
        # method: HTTP method for the call
        self._method = get_conf_value(data, 'method', 'GET').upper()
        # payload: body for the call
        self._payload = get_conf_value(data, 'payload')
        # params: URL parameters
        self._params = get_conf_value(data, 'params')
        # headers
        shared_headers = get_conf_value(shared_config, 'headers', [])
        test_headers = get_headers_list(data)
        self._headers = merge_headers_lists(shared_headers, test_headers)
        # expected: path to file containing the expected result body for the call. File content interpreted as json
        self._expected_result_file = get_conf_value(data, 'expected')
        if self._expected_result_file is None or self._expected_result_file == '':
            raise ValueError('[Test {}] Missing expected result file'.format(self._name))
        if self._expected_result_file[0] != '/':
            self._expected_result_file = os.path.join(os.getcwd(), self._expected_result_file)
        if not os.path.exists(self._expected_result_file):
            raise FileNotFoundError('[Test {}] Could not find expected result file: "{}"'.format(self._name, self._expected_result_file))
        with open(self._expected_result_file, 'r', encoding='utf-8') as res:
            self._expected_result = json.load(res)
        # expected_code: the expected status code the call should return
        self._expected_result_code = get_conf_value(data, 'expected_code', 200)
        # response_check_exceptions: list of fields in the response body to ignore when checking the result
        self._response_check_exceptions = get_conf_value(data, 'responseCheckExceptions', [])
        # extract: list of fields to extract from the response
        self._extract = get_conf_value(data, 'extract', [])
        # inject: list of fields we need to have injected for the call to be successful
        self._inject = get_conf_value(data, 'inject', [])

    def _get_headers(self) -> Dict[str, Any]:
        '''
        Return headers to use for the call

        :return: Headers for the API call
        :rtype:  Dict[str, Any]
        '''
        heads = {}
        for h in self._headers: # type: Header
            if not h.hide:
                heads[h.key] = h.value
        return heads

    def _inject_body(self, value_key: str, injecting_value: Any):
        '''
        Inject value into request body

        :param value_key:       Body key in payload
        :type value_key:        str
        :param injecting_value: Value to inject into the body
        :type injecting_value:  Any
        '''
        set_inner_key_value(self._payload, value_key, injecting_value)

    def _inject_query(self, value_key: str, injecting_value: Any):
        '''
        Inject value into request params

        :param value_key:       key of the url parameter
        :type value_key:        str
        :param injecting_value: Value to inject into the request parameter
        :type injecting_value:  Any
        '''
        if self._params is None:
            self._params = {}
        self._params[value_key] = injecting_value

    def _inject_path(self, injecting_value: Any):
        '''
        Inject value as url path

        :param injecting_value: Value to inject into the url path
        :type injecting_value:  Any
        '''
        if self._url[-1] == '/':
            self._url = self._url[:-1]
        self._url += '/{}'.format(injecting_value)

    def _inject_header(self, value_key: str, injecting_value: Any):
        '''
        Inject value into request headers

        :param value_key:       key of the header
        :type value_key:        str
        :param injecting_value: Value to inject into the request header
        :type injecting_value:  Any
        '''
        for h in self._headers:
            if h.key == value_key:
                h.value = injecting_value
                break
        else: # no break
            self._headers.append(Header(value_key, { 'value': injecting_value }))

    # -----------------------
    # ----- Properties ------
    # -----------------------

    @property
    def enabled(self) -> bool:
        '''
        Return whether to run this test or not

        :return: Whether to run this test or not
        :rtype:  bool
        '''
        return self._enabled

    @property
    def name(self) -> str:
        '''
        Return this test name

        :return: This test name
        :rtype:  str
        '''
        return self._name

    @property
    def status(self) -> TestStatus:
        '''
        Return this test status

        :return: This test status
        :rtype:  TestStatus
        '''
        return self._status
