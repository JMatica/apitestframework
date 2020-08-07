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
from typing import Any, Dict

# local imports
from apitestframework.utils.config import get_conf_value

logger = logging.getLogger(__name__)

class Header(object):
    '''
    A HTTP Header class, sugar coated
    '''

    def __init__(self, key: str, data: Dict[str, Any]):
        '''
        Initialize Header

        :param key:  The key of the header
        :type key:   str
        :param data: Configuration object
        :type data:  Dict[str, Any]
        '''
        self._key = key
        self._hide = get_conf_value(data, 'hide', False)
        self._orig_value = get_conf_value(data, 'value', '')
        self._value = self._orig_value
        self._placeholder = get_conf_value(data, 'placeholder', '{}')
        env_name = get_conf_value(data, 'envName')
        # replace placeholder with correct value, if needed
        if self._placeholder in self._orig_value and env_name is not None:
            env = os.environ.get(env_name)
            if env is not None:
                logger.debug('Filling "{}" Header value ({}) with environment variable {}'.format(key, env, env_name))
                self._value = self._orig_value.replace(self._placeholder, env)
            else:
                logger.warn('"{}" Header value cannot be filled with environment variable {}: Not found in system'.format(key, env_name))

    # -----------------------
    # ----- Properties ------
    # -----------------------

    @property
    def key(self) -> str:
        '''
        Return this header key

        :return: This header key
        :rtype:  str
        '''
        return self._key

    @property
    def value(self) -> str:
        '''
        Return this header value

        :return: This header value
        :rtype:  str
        '''
        return self._value

    @value.setter
    def value(self, new_value: str):
        '''
        Update the value of this header with the given one.
        If a placeholder was present in the header definition, only that part will be updated

        :param new_value: The new value for the header
        :type new_value:  str
        '''
        if self._placeholder in self._orig_value:
            self._value = self._orig_value.replace(self._placeholder, new_value)
        else:
            self._value = new_value

    @property
    def hide(self) -> bool:
        '''
        Return whether to hide this header from the call

        :return: Whether to hide this header from the call
        :rtype:  bool
        '''
        return self._hide
