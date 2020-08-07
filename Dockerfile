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

# python 3.7
FROM python:3

# prepare folder
RUN mkdir -p /tmpdata
# copy egg and requirements file
COPY src/requirements.txt src/dist/*.tar.gz /tmpdata/

# install application and remove temp data
RUN pip install -r /tmpdata/requirements.txt && \
    pip install /tmpdata/*.tar.gz && \
    rm -rf /tmpdata

# volume to mount to be able to accept external configuration files
VOLUME ["/config"]
# default config file
ENV CONFIG_FILE=config.json
# command to launch at container startup
ENTRYPOINT python -m apitestframework "/config/$CONFIG_FILE"
