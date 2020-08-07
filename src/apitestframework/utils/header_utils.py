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
from typing import Any, Dict, List

# local imports
from apitestframework.utils.config import get_conf_value
from apitestframework.utils.header import Header

def get_headers_list(data: Dict[str, Any]) -> List[Header]:
    '''
    Extract Header information from configuration

    :param data: Configuration object containing header information
    :type data:  Dict[str, Any]

    :return: Headers extracted from configuration
    :rtype:  List[Header]
    '''
    headers = []
    heads = get_conf_value(data, 'headers', {})
    for key in heads.keys():
        headers.append(Header(key, heads[key]))
    return headers

def merge_headers_lists(list_a: List[Header], list_b: List[Header]) -> List[Header]:
    '''
    Merge two lists of headers removing duplicates. list_b overwrites list_a

    :param list_a: List of headers to augment
    :type list_a:  List[Header]
    :param list_a: List of headers to add to the first
    :type list_a:  List[Header]

    :return: List of Headers without duplicates
    :rtype:  List[Header]
    '''
    headers_list = []
    a_keys = set([h.key for h in list_a])
    b_keys = set([h.key for h in list_b])
    shared_keys = a_keys.intersection(b_keys)
    # headers in list_a not present in list_b
    for ha in list_a:
        if ha.key not in shared_keys:
            headers_list.append(ha)
    # headers in list_b not present in list_a
    for hb in list_b:
        if hb.key not in shared_keys:
            headers_list.append(hb)
    # TODO optimize this
    for ha in list_a:
        for hb in list_b:
            if ha.key in shared_keys and ha.key == hb.key:
                headers_list.append(hb)
    return headers_list
