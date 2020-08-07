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
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

# local imports
from apitestframework.core.test_suite import TestSuite
from apitestframework.utils.config import get_conf_value
from apitestframework.utils.header_utils import get_headers_list
from apitestframework.utils.test_status import TestStatus

logger = logging.getLogger(__name__)

class TestRun(object):
    '''
    Collection of test suites
    '''

    def __init__(self, config: Dict[str, Any]):
        '''
        Initialize test run

        :param config: Configuration object
        :type config:  Dict[str, Any]
        '''
        suites_def = get_conf_value(config, 'suites', [])
        global_config = self._get_global_config(config)
        self._suites = []
        for sc in suites_def:
            self._suites.append(TestSuite(sc, global_config))

    # ---------------------------
    # ----- Public methods ------
    # ---------------------------

    def run(self):
        '''
        Run all the test suites
        '''
        logger.info('')
        logger.info('Starting Test Run at {0:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
        # run test suites
        for s in self._suites:
            s.run()
        run_result = self._summary()
        # exit with error if a test failed
        if not run_result:
            sys.exit(1)

    # ----------------------------
    # ----- Private methods ------
    # ----------------------------

    def _get_global_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Initialize configuration shared by all objects in this test run

        :param config: Configuration object
        :type config:  Dict[str, Any]

        :return: A dictionary containing all the available global configuration sections
        :rtype:  Dict[str, Any]
        '''
        return {
            'headers': get_headers_list(config)
        }

    def _summary(self) -> bool:
        '''
        Print a summary of the test run

        :return: Whether all tests were successful or not
        :rtype:  bool
        '''
        status_success_acc = True
        logger.info('')
        logger.info('Test Run finished at {0:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
        logger.info('')
        logger.info('---------- Test run Results ----------')
        for s in self._suites:
            logger.info('')
            logger.info('**************************************************')
            logger.info('Test Suite "{}"'.format(s.name))
            logger.info('**************************************************')
            for tr in s.test_results:
                (test_name, result_test_status, _) = tr
                test_success = (result_test_status != TestStatus.FAILURE)
                status_success_acc = status_success_acc and test_success
                logger.info('{} Test "{}" - Result: {}'.format(result_test_status.icon(), test_name, result_test_status.name))
        logger.info('')
        if not status_success_acc:
            logger.error('Some tests failed. See the results above for more details.')
        else:
            logger.info('All tests successful. See the results above for more details.')
        logger.info('')
        logger.info('-----------------------------------')
        logger.info('')
        return status_success_acc
