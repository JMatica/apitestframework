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
import signal
import sys
from typing import Any, Dict

# local imports
from apitestframework.core.test_run import TestRun
from apitestframework.utils.config import get_conf_value, load_config

logger = None

def signal_handler(sig: int, frame):
    '''
    Manages exit codes to do proper clean up

    :param sig:   The signal number
    :type sig:    int
    :param frame: The current stack frame
    :type frame:  Frame object
    '''
    logger.warn('Handling signal {} before exiting!'.format(sig))
    sys.exit(0)

def boot(config: Dict[str, Any]):
    '''
    Module starting point.

    Setup what's needed and start the program

    :param config: Configuration object
    :type config:  Dict[str, Any]
    '''
    # setup logger
    setup_logging(config)
    # setup test run
    test_run = TestRun(config)
    test_run.run()

def setup_logging(config: Dict[str, Any]):
    '''
    Setup loggers.

    :param config: Configuration object
    :type config:  Dict[str, Any]
    '''
    global logger
    handlers = []

    # setup console logger
    # possible format :-> [%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
    console_formatter = logging.Formatter('[%(asctime)s] %(message)s')
    console = logging.StreamHandler()
    console.setLevel(get_conf_value(config, 'logLevel', 10))
    console.setFormatter(console_formatter)
    handlers.append(console)

    logging.basicConfig(handlers=handlers, level=logging.DEBUG)
    logger = logging.getLogger(__name__)

def main():
    '''
    Program entry point
    '''
    # setup for signal trapping
    signal.signal(signal.SIGINT, signal_handler)
    # start up with command line arguments check
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            config_file = arg
            config = load_config(config_file)
            boot(config)
    else:
        sys.exit('Missing configuration file (json format).')

if __name__ == '__main__':
    # start program
    main()
