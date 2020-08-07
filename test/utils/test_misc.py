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
from apitestframework.utils.misc import build_keys_list, camel_to_snake, get_inner_key_value, set_inner_key_value

class TestMisc(object):
    '''
    Test utils.misc module
    '''

    def test_camel_to_snake(self):
        '''
        Test camel_to_snake method
        '''
        assert camel_to_snake('camel') == 'camel'
        assert camel_to_snake('Camel') == 'camel'
        assert camel_to_snake('cameL') == 'came_l'
        assert camel_to_snake('camelCase') == 'camel_case'
        assert camel_to_snake('CamelCase') == 'camel_case'

    def test_build_keys_list(self):
        '''
        Test test_build_keys_list method
        '''
        data = {
            'id': 'some_id',
            'solutions': [
                {
                    'solutionId': 'VCC-2001-09400-59700-1567116000',
                    'departureStationCode': '09400',
                    'arrivalStationCode': '59700',
                    'departureDateTime': '2019-08-30T10:00:00+02:00',
                    'arrivalDateTime': '2019-08-30T12:40:00+02:00',
                    'segments': [
                        {
                            'departureStationCode': '09400',
                            'arrivalStationCode': '67000',
                            'departureDateTime': '2019-08-30T10:00:00+02:00',
                            'arrivalDateTime': '2019-08-30T12:15:00+02:00',
                            'carrier': 'ATVO Spa',
                            'line': 'Venezia Cortina Commerciale',
                            'travelMode': 'bus'
                        }
                    ]
                }
            ],
            'money': {
                'currency': 'EUR',
                'price': 32.5,
            }
        }
        keys = [
            'id',
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
            "solutions.0.segments.0.travelMode",
            "money.currency",
            "money.price",
        ]
        assert build_keys_list(data) == keys
        assert build_keys_list() == []
        assert build_keys_list({}) == []

    def test_get_inner_key_value(self):
        '''
        Test get_inner_key_value method
        '''
        data = {
            'currency': 'EUR',
            'price': 32.5,
            'solutions': [
                {
                    'solutionId': 'VCC-2001-09400-59700-1567116000',
                    'departureStationCode': '09400',
                    'arrivalStationCode': '59700',
                    'departureDateTime': '2019-08-30T10:00:00+02:00',
                    'arrivalDateTime': '2019-08-30T12:40:00+02:00',
                    'segments': [
                        {
                            'departureStationCode': '09400',
                            'arrivalStationCode': '67000',
                            'departureDateTime': '2019-08-30T10:00:00+02:00',
                            'arrivalDateTime': '2019-08-30T12:15:00+02:00',
                            'carrier': 'ATVO Spa',
                            'line': 'Venezia Cortina Commerciale',
                            'travelMode': 'bus'
                        }
                    ]
                }
            ]
        }
        assert get_inner_key_value(data, None) is None
        assert get_inner_key_value(None, 'currency') is None
        assert get_inner_key_value(None, None) is None
        assert get_inner_key_value(data, 'currency') == 'EUR'
        assert get_inner_key_value(data, 'price') == 32.5
        assert get_inner_key_value(data, 'solutions.0.departureStationCode') == '09400'
        assert get_inner_key_value(data, 'solutions.0.segments.0.carrier') == 'ATVO Spa'
        assert isinstance(get_inner_key_value(data, 'solutions'), list) == True
        assert isinstance(get_inner_key_value(data, 'solutions.0'), dict) == True
        assert get_inner_key_value(data, 'solutions.0.ghost.phantom') is None
        assert get_inner_key_value(data, 'solutions.2') is None

    def test_set_inner_key_value(self):
        '''
        Test set_inner_key_value method
        '''
        data = {
            'currency': 'EUR',
            'price': 32.5,
            'solutions': [
                {
                    'solutionId': 'VCC-2001-09400-59700-1567116000',
                    'departureStationCode': '09400',
                    'arrivalStationCode': '59700',
                    'departureDateTime': '2019-08-30T10:00:00+02:00',
                    'arrivalDateTime': '2019-08-30T12:40:00+02:00',
                    'segments': [
                        {
                            'departureStationCode': '09400',
                            'arrivalStationCode': '67000',
                            'departureDateTime': '2019-08-30T10:00:00+02:00',
                            'arrivalDateTime': '2019-08-30T12:15:00+02:00',
                            'carrier': 'ATVO Spa',
                            'line': 'Venezia Cortina Commerciale',
                            'travelMode': 'bus'
                        }
                    ],
                    'others': {
                        'mysticId': 42
                    }
                }
            ]
        }
        set_inner_key_value(data, 'price', 10)
        assert get_inner_key_value(data, 'price') == 10
        set_inner_key_value(data, 'solutions.0.departureStationCode', '12345')
        assert get_inner_key_value(data, 'solutions.0.departureStationCode') == '12345'
        set_inner_key_value(data, 'solutions.0.segments', [])
        assert get_inner_key_value(data, 'solutions.0.segments') == []
        set_inner_key_value(data, 'solutions.1.departureStationCode', '123456')
        assert get_inner_key_value(data, 'solutions.1.departureStationCode') is None
        set_inner_key_value(data, 'id', 10)
        assert get_inner_key_value(data, 'id') == 10
        set_inner_key_value(data, 'solutions.0.solutionId.id', 10)
        assert get_inner_key_value(data, 'solutions.0.solutionId.id') == None
        set_inner_key_value(data, 'solutions.0.solutionId.id.subId', 10)
        assert get_inner_key_value(data, 'solutions.0.solutionId.id.subId') == None
        set_inner_key_value(data, 'solutions.0.alternativeFactId', 420)
        assert get_inner_key_value(data, 'solutions.0.alternativeFactId') == 420
        set_inner_key_value(data, 'solutions.0.others.pupil.normalId', 33)
        assert get_inner_key_value(data, 'solutions.0.others.pupil.normalId') is None
