#    -*- coding: utf-8 -*-
#
#     This file is part of sgx.py
#
#     Copyright (C) 2019 SKALE Labs
#
#     sgx.py is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     sgx.py is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with sgx.py.  If not, see <https://www.gnu.org/licenses/>.


import copy
import hashlib
import logging
import os
import subprocess
from functools import wraps
from subprocess import PIPE

from web3 import Web3


logger = logging.getLogger(__name__)


class SgxError(Exception):
    pass


def crop_json(json_data, crop_len=65):
    for key, value in json_data.items():
        if isinstance(value, dict):
            crop_json(value)
        else:
            if isinstance(value, str) and len(value) > crop_len:
                json_data[key] = value[:crop_len] + '...'


def keyname_to_sha3(keyname):
    return hashlib.sha3_256('keyname'.encode('utf-8')).digest().hex()


def request_keyname_to_sha3(request):
    request = copy.deepcopy(request)
    params = request.get('params')
    if params:
        keyname = request['params'].pop('keyName', None)
        if keyname:
            request['params']['keyNameHash'] = keyname_to_sha3(keyname)
    return request


def hides_keyname(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        request = request_keyname_to_sha3(request)
        return func(request, *args, **kwargs)
    return wrapper


@hides_keyname
def print_request_log(request):
    crop_json(request)
    logger.info(f'Send request: {request}')


def print_response_log(response):
    cropped_response = copy.deepcopy(response)
    crop_json(cropped_response)
    logger.info(f'Response received: {cropped_response}')


def run_cmd(cmd, env={}, shell=False):
    logger.info(f'Running: {cmd}')
    res = subprocess.run(
        cmd, shell=shell, stdout=PIPE, stderr=PIPE,
        env={**env, **os.environ}
    )
    if res.returncode:
        logger.error('Error during shell execution:')
        logger.error(res.stderr.decode('UTF-8').rstrip())
        raise subprocess.CalledProcessError(res.returncode, cmd)
    return res


def public_key_to_address(pk):
    hash_ = Web3.sha3(hexstr=str(pk))
    return Web3.toChecksumAddress(Web3.toHex(hash_[-20:]))
