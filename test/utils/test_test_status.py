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
from apitestframework.utils.test_status import TestStatus

class TestTestStatus(object):
    '''
    Test utils.test_status module
    '''

    def test_icon(self):
        '''
        Test icon method
        '''
        assert TestStatus.PENDING.icon() == '⧖'
        assert TestStatus.RUNNING.icon() == '▶'
        assert TestStatus.SUCCESS.icon() == '✔'
        assert TestStatus.FAILURE.icon() == '✘'
        assert TestStatus.SKIPPED.icon() == '◉'
        assert TestStatus.UNKNOWN.icon() == '?'
