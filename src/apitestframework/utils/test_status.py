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

from enum import IntEnum, unique

@unique
class TestStatus(IntEnum):
    '''
    Status of a Test
    '''
    # test not executed yet
    PENDING = 0
    # test in execution
    RUNNING = 1
    # test executed successfully
    SUCCESS = 2
    # test executed with failures
    FAILURE = 3
    # test skipped
    SKIPPED = 4
    # unknown
    UNKNOWN = 39

    def icon(self) -> str:
        '''
        Return a unicode symbol representing the status

        :return: A code representing the status
        :rtype:  str
        '''
        if self == TestStatus.PENDING:
            return '\N{White Hourglass}'
        elif self == TestStatus.RUNNING:
            return '\N{Black Right-Pointing Triangle}'
        elif self == TestStatus.SUCCESS:
            return '\N{Heavy Check Mark}'
        elif self == TestStatus.FAILURE:
            return '\N{Heavy Ballot X}'
        elif self == TestStatus.SKIPPED:
            return '\N{Fisheye}'
        else:
            return '\N{Question Mark}'
