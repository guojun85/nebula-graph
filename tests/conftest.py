# --coding:utf-8--
#
# Copyright (c) 2020 vesoft inc. All rights reserved.
#
# This source code is licensed under Apache 2.0 License,
# attached with Common Clause Condition 1.0, found in the LICENSES directory.

import pytest
import os
import logging

DOCKER_GRAPHD_DIGESTS = os.getenv('NEBULA_GRAPHD_DIGESTS')
if DOCKER_GRAPHD_DIGESTS is None:
    DOCKER_GRAPHD_DIGESTS = '0'
DOCKER_METAD_DIGESTS = os.getenv('NEBULA_METAD_DIGESTS')
if DOCKER_METAD_DIGESTS is None:
    DOCKER_METAD_DIGESTS = '0'
DOCKER_STORAGED_DIGESTS = os.getenv('NEBULA_STORAGED_DIGESTS')
if DOCKER_STORAGED_DIGESTS is None:
    DOCKER_STORAGED_DIGESTS = '0'

tests_collected = set()
tests_executed = set()
data_dir = os.getenv('NEBULA_DATA_DIR')

# pytest hook to handle test collection when xdist is used (parallel tests)
# https://github.com/pytest-dev/pytest-xdist/pull/35/commits (No official documentation available)
def pytest_xdist_node_collection_finished(node, ids):
    tests_collected.update(set(ids))

# link to pytest_collection_modifyitems
# https://docs.pytest.org/en/5.3.2/writing_plugins.html#hook-function-validation-and-execution
@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    for item in items:
        tests_collected.add(item.nodeid)

# link to pytest_runtest_logreport
# https://docs.pytest.org/en/5.3.2/reference.html#_pytest.hookspec.pytest_runtest_logreport
def pytest_runtest_logreport(report):
    if report.passed:
        tests_executed.add(report.nodeid)

def pytest_addoption(parser):
    parser.addoption('--address',
                         dest='address',
                         default="127.0.0.1:3699",
                         help="address of the Nebula")
    parser.addoption('--user',
                        dest='user',
                        default='user',
                        help='the user of Nebula')
    parser.addoption('--password',
                        dest='password',
                        default='password',
                        help='the password of Nebula')
    parser.addoption('--partition_num',
                        dest='partition_num',
                        default=10,
                        help='the partition_num of Nebula\'s space')
    parser.addoption('--replica_factor',
                        dest='replica_factor',
                        default=1,
                        help='the replica_factor of Nebula\'s space')
    parser.addoption('--data_dir',
                        dest='data_dir',
                        help='Data Preload Directory for Nebula')

    parser.addoption('--stop_nebula',
                        dest='stop_nebula',
                        default='true',
                        help='Stop the nebula services')

    parser.addoption('--rm_dir',
                        dest='rm_dir',
                        default='true',
                        help='Remove the temp test dir')

    parser.addoption('--debug_log',
                         dest='debug_log',
                         default='true',
                         help='set nebula service --v=4')

def pytest_configure(config):
    pytest.cmdline.address = config.getoption("address")
    pytest.cmdline.user = config.getoption("user")
    pytest.cmdline.password = config.getoption("password")
    pytest.cmdline.replica_factor = config.getoption("replica_factor")
    pytest.cmdline.partition_num = config.getoption("partition_num")
    if data_dir is None:
        pytest.cmdline.data_dir = config.getoption("data_dir")
    else:
        pytest.cmdline.data_dir = data_dir
    pytest.cmdline.stop_nebula = config.getoption("stop_nebula")
    pytest.cmdline.rm_dir = config.getoption("rm_dir")
    pytest.cmdline.debug_log = config.getoption("debug_log")
    config._metadata['graphd digest'] = DOCKER_GRAPHD_DIGESTS
    config._metadata['metad digest'] = DOCKER_METAD_DIGESTS
    config._metadata['storaged digest'] = DOCKER_STORAGED_DIGESTS
