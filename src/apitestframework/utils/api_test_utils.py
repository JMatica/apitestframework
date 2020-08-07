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
import traceback
from typing import Any, Dict, List

# local imports
from apitestframework.utils.misc import build_keys_list, get_inner_key_value

logger = logging.getLogger(__name__)

def check_result_content(result: Dict[str, Any], expected: Dict[str, Any], expected_result_file: str = None, exceptions: List[str] = None) -> bool:
    '''
    Check the API call result content against the expected content

    :param result:   The actual API call result
    :type result:    Dict[str, Any]
    :param expected: The expected API call result
    :type expected:  Dict[str, Any]

    :return: The resulting status of the test
    :rtype:  bool
    '''
    if expected_result_file is None:
        expected_result_file = 'N/A'
    if exceptions is None:
        exceptions = []
    logger.debug('Checking test result content...')
    test_status = True
    expected_keys_list = build_keys_list(expected)
    # check all keys in expected
    for k in expected_keys_list:
        # do not check for content if in ignore list
        exc = next((e for e in exceptions if e['key'] == k), None)
        if exc is None:
            # get actual and expected values
            result_value = get_inner_key_value(result, k)
            expected_value = get_inner_key_value(expected, k)
            # check
            if result_value != expected_value:
                logger.error('Check Result failed for key {} :: expected: {} - actual: {}'.format(k, expected_value, result_value))
                test_status = False
        else:
            logger.debug('Key {} found in exceptions list'.format(k))
            exc_type = exc['type']
            if exc_type == 'ignore':
                continue
            elif exc_type == 'exist':
                result_keys_list = build_keys_list(result)
                if k not in result_keys_list:
                    test_status = False
    # check final result
    if not test_status:
        logger.error('Content check failed')
        logger.error('Expected result (file {}) was :: {}'.format(expected_result_file, expected))
        logger.error('Actual result was :: {}'.format(result))
    else:
        logger.debug('Content check successful.')
    # return final test status
    return test_status

def check_result_code(result_code: int, expected_code: int) -> bool:
    '''
    Check the API call result status code against the expected status code

    :param result_code:   The actual API call result status code
    :type result_code:    int
    :param expected_code: The expected API call result status code
    :type expected_code:  int

    :return: The result of the test
    :rtype:  bool
    '''
    logger.debug('Checking test result code...')
    # check final result
    test_code_status = (result_code == expected_code)
    if not test_code_status:
        logger.error('Code check failed')
        logger.error('Expected code was :: {}'.format(expected_code))
        logger.error('Actual result was :: {}'.format(result_code))
    else:
        logger.debug('Code check successful.')
    # return final test status
    return test_code_status
