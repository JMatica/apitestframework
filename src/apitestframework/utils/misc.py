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
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

def get_inner_key_value(data: Dict[str, Any], key: str) -> Any:
    '''
    Retrieve the value of a key nested N-levels down from a dictionary

    :param data: The dictionary containing the values
    :type data:  Dict[str, Any]
    :param key:  The key in dot notation. I.e. "one.two.three"
    :type key:   str

    :return: The value of the requested key
    :rtype:  Any
    '''
    if data is None or key is None:
        return None
    keys = key.split('.')
    d = data
    for k in keys:
        try:
            k = int(k)
        except ValueError:
            # not a number, just a string
            pass
        try:
            if isinstance(k, int) and isinstance(d, list) and k >= len(d):
                # index out of range
                return None
            d = d[k]
        except KeyError:
            # key not present
            return None
        except TypeError:
            # wrong type of index
            return None
    return d

def set_inner_key_value(data: Dict[str, Any], key: str, value: Any):
    '''
    Set the value of a key nested N-levels down into a dictionary

    :param data:  The dictionary containing the values
    :type data:   Dict[str, Any]
    :param key:   The key in dot notation. I.e. "one.two.three"
    :type key:    str
    :param value: The value to set for the key
    :type value:  Any
    '''
    if data is None or key is None:
        return
    keys = key.split('.')
    d = data
    for k in keys[:-1]:
        try:
            k = int(k)
        except ValueError:
            # not a number, just a string
            pass
        try:
            if isinstance(k, int) and isinstance(d, list) and k >= len(d):
                # index out of range
                return
            d = d[k]
        except KeyError:
            # key not present
            return
        except TypeError:
            # wrong type of index
            return
    try:
        d[keys[-1]] = value
    except TypeError:
        # trying to assign to something that cannot be assigned
        return

def build_keys_list(data: Dict[str, Any] = None) -> List[str]:
    '''
    Given a dictionary, build a list of all its keys in dot notation.

    E.g. for the following dictionary:
    a = {
        "currency": "EUR",
        "solutions": [
            {
                "solutionId": "VCC-2001-09400-59700-1567116000",
                "departureStationCode": "09400",
                "arrivalStationCode": "59700",
                "departureDateTime": "2019-08-30T10:00:00+02:00",
                "arrivalDateTime": "2019-08-30T12:40:00+02:00",
                "segments": [
                    {
                        "departureStationCode": "09400",
                        "arrivalStationCode": "67000",
                        "departureDateTime": "2019-08-30T10:00:00+02:00",
                        "arrivalDateTime": "2019-08-30T12:15:00+02:00",
                        "carrier": "ATVO Spa",
                        "line": "Venezia Cortina Commerciale",
                        "travelMode": "bus"
                    }
                ]
            }
        ]
    }
    The result would be:
    res = [
        "currency",
        "solutions.0.solutionId",
        "solutions.0.departureStationCode",
        "solutions.0.arrivalStationCode",
        "solutions.0.departureDateTime",
        "solutions.0.arrivalDateTime",
        "solutions.0.segments.0.departureStationCode",
        "solutions.0.segments.0.arrivalStationCode",
        "solutions.0.segments.0.departureDateTime",
        "solutions.0.segments.0.arrivalDateTime",
        "solutions.0.segments.0.carrier",
        "solutions.0.segments.0.line",
        "solutions.0.segments.0.travelMode"
    ]

    :param data: The source dictionary
    :type data:  Dict[str, Any]

    :return: A list of all the keys in the dict in dot notation
    :rtype:  List[str]
    '''

    if data is None:
        return []
    keys = []
    data_keys = data.keys()
    for k in data_keys:
        e = data[k]
        if _is_primitive(e):
            # primitive type
            keys.append(k)
        elif isinstance(e, dict):
            # nested dictionary
            nested_dict_keys = build_keys_list(e)
            for ndk in nested_dict_keys:
                keys.append('{}.{}'.format(k, ndk))
        elif isinstance(e, list):
            # nested list
            for i in range(len(e)):
                nested_list_keys = build_keys_list(e[i])
                for nlk in nested_list_keys:
                    keys.append('{}.{}.{}'.format(k, i, nlk))
    return keys

# RegExp for converting string from camelCase to snake_case
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def camel_to_snake(name: str) -> str:
    '''
    Convert a string from camelCase to snake_case

    :param name: The string to convert
    :type name:  str

    :return: The given string converted to snake_case
    :rtype:  str
    '''
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def _is_primitive(el: Any) -> bool:
    '''
    Return whether the element is a primitive type

    :param el: The element to test
    :type el:  Any

    :return: Whether the element is a primitive type
    :rtype:  bool
    '''
    return isinstance(el, str) or isinstance(el, int) or isinstance(el, float) or isinstance(el, bool)
