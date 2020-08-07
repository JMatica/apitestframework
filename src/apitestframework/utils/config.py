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
import sys
from typing import Any, Dict

logger = logging.getLogger(__name__)

def load_config(config_file: str) -> Dict[str, Any]:
    '''
    Load configuration from input file

    Exit if file does not exist on file system

    :param config_path: The path to the configuration file
    :type config_path:  str

    :return: The configuration object
    :rtype:  Dict[str, Any]
    '''
    try:
        config_path = os.path.abspath(config_file)
        # check if config file exists
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding="utf-8") as j:
                logger.debug('Loading configuration file {}'.format(config_path))
                config = json.load(j)
            return config
        else:
            sys.exit('Missing configuration file (json format).\n\nPlease make sure the file {} exists.'.format(config_file))
    except:
        raise

def get_conf_value(data: Dict[str, Any], key: str, default_value: Any = None) -> Any:
    '''
    Return the value of a configuration key or, if not found, a default value

    :param data:          The source data
    :type data:           Dict[str, Any]
    :param key:           The key to retrieve from data
    :type key:            str
    :param default_value: Default value to return if the key is not found
    :type default_value:  Any

    :return: A value from the configuration
    :rtype:  Any
    '''
    # return value if found
    if data is not None and key in data:
        return data[key]
    # otherwise return default
    if default_value is not None:
        return default_value
    # otherwise is just as well. implicitly returning None
