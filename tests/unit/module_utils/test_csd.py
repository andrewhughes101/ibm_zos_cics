# -*- coding: utf-8 -*-

# (c) Copyright IBM Corp. 2023,2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dd_statement import StdinDefinition
from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils._data_set import CYLINDERS, MEGABYTES
from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils._response import MVSExecutionException, _execution
from ansible_collections.ibm.ibm_zos_cics.tests.unit.helpers.data_set_helper import (
    PYTHON_LANGUAGE_FEATURES_MESSAGE,
    CSDUP_name,
    CSDUP_stderr,
    CSDUP_initialize_stdout
)
from ansible_collections.ibm.ibm_zos_cics.plugins.modules.csd import SPACE_PRIMARY_DEFAULT, SPACE_SECONDARY_DEFAULT

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.zos_mvs_raw import MVSCmdResponse

__metaclass__ = type
from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils import _csd as csd
from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils import _data_set_utils as data_set_utils
import pytest
import sys

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


NAME = "ANSI.TEST.DFHCSD"


def setUp():
    StdinDefinition.__init__ = MagicMock(return_value=None)


@pytest.mark.skipif(sys.version_info.major < 3, reason=PYTHON_LANGUAGE_FEATURES_MESSAGE)
def test_get_idcams_cmd_megabytes():
    csd_data_set = dict(
        name=NAME,
        sdfhload="CICSTS.IN56.SDFHLOAD",
        state="initial",
        exists=False,
        data_set_organization="NONE",
        unit=MEGABYTES,
        primary=SPACE_PRIMARY_DEFAULT,
        secondary=SPACE_SECONDARY_DEFAULT
    )
    idcams_cmd_csd = data_set_utils._build_idcams_define_cmd(csd._get_idcams_cmd_csd(csd_data_set))
    assert idcams_cmd_csd == '''
    DEFINE CLUSTER (NAME(ANSI.TEST.DFHCSD) -
    MEGABYTES(4 1) -
    RECORDSIZE(200 2000) -
    INDEXED -
    KEYS(22 0) -
    FREESPACE(10 10) -
    SHAREOPTIONS(2) -
    REUSE) -
    DATA (NAME(ANSI.TEST.DFHCSD.DATA) -
    CONTROLINTERVALSIZE(8192)) -
    INDEX (NAME(ANSI.TEST.DFHCSD.INDEX))
    '''


@pytest.mark.skipif(sys.version_info.major < 3, reason=PYTHON_LANGUAGE_FEATURES_MESSAGE)
def test_get_idcams_cmd_cylinders():
    csd_data_set = dict(
        name=NAME,
        sdfhload="CICSTS.IN56.SDFHLOAD",
        state="initial",
        exists=False,
        data_set_organization="NONE",
        unit=CYLINDERS,
        primary=SPACE_PRIMARY_DEFAULT,
        secondary=SPACE_SECONDARY_DEFAULT
    )
    idcams_cmd_csd = data_set_utils._build_idcams_define_cmd(csd._get_idcams_cmd_csd(csd_data_set))
    assert idcams_cmd_csd == '''
    DEFINE CLUSTER (NAME(ANSI.TEST.DFHCSD) -
    CYLINDERS(4 1) -
    RECORDSIZE(200 2000) -
    INDEXED -
    KEYS(22 0) -
    FREESPACE(10 10) -
    SHAREOPTIONS(2) -
    REUSE) -
    DATA (NAME(ANSI.TEST.DFHCSD.DATA) -
    CONTROLINTERVALSIZE(8192)) -
    INDEX (NAME(ANSI.TEST.DFHCSD.INDEX))
    '''


@pytest.mark.skipif(sys.version_info.major < 3, reason=PYTHON_LANGUAGE_FEATURES_MESSAGE)
def test_get_idcams_cmd_backout_recovery():
    csd_data_set = dict(
        name=NAME,
        sdfhload="CICSTS.IN56.SDFHLOAD",
        state="initial",
        exists=False,
        data_set_organization="NONE",
        unit=MEGABYTES,
        primary=SPACE_PRIMARY_DEFAULT,
        secondary=SPACE_SECONDARY_DEFAULT,
        log="UNDO"
    )
    idcams_cmd_csd = data_set_utils._build_idcams_define_cmd(csd._get_idcams_cmd_csd(csd_data_set))
    assert idcams_cmd_csd == '''
    DEFINE CLUSTER (NAME(ANSI.TEST.DFHCSD) -
    MEGABYTES(4 1) -
    RECORDSIZE(200 2000) -
    INDEXED -
    KEYS(22 0) -
    FREESPACE(10 10) -
    SHAREOPTIONS(2) -
    REUSE -
    LOG(UNDO)) -
    DATA (NAME(ANSI.TEST.DFHCSD.DATA) -
    CONTROLINTERVALSIZE(8192)) -
    INDEX (NAME(ANSI.TEST.DFHCSD.INDEX))
    '''


@pytest.mark.skipif(sys.version_info.major < 3, reason=PYTHON_LANGUAGE_FEATURES_MESSAGE)
def test_get_idcams_cmd_forward_recovery():
    csd_data_set = dict(
        name=NAME,
        sdfhload="CICSTS.IN56.SDFHLOAD",
        state="initial",
        exists=False,
        data_set_organization="NONE",
        unit=MEGABYTES,
        primary=SPACE_PRIMARY_DEFAULT,
        secondary=SPACE_SECONDARY_DEFAULT,
        log="ALL",
        logstream_id="TEST.DATA.LOG.STREAM"
    )
    idcams_cmd_csd = data_set_utils._build_idcams_define_cmd(csd._get_idcams_cmd_csd(csd_data_set))
    assert idcams_cmd_csd == '''
    DEFINE CLUSTER (NAME(ANSI.TEST.DFHCSD) -
    MEGABYTES(4 1) -
    RECORDSIZE(200 2000) -
    INDEXED -
    KEYS(22 0) -
    FREESPACE(10 10) -
    SHAREOPTIONS(2) -
    REUSE -
    LOG(ALL) -
    LOGSTREAMID(TEST.DATA.LOG.STREAM)) -
    DATA (NAME(ANSI.TEST.DFHCSD.DATA) -
    CONTROLINTERVALSIZE(8192)) -
    INDEX (NAME(ANSI.TEST.DFHCSD.INDEX))
    '''


@pytest.mark.skipif(sys.version_info.major < 3, reason=PYTHON_LANGUAGE_FEATURES_MESSAGE)
def test_get_idcams_cmd_backout_recovery_logstream_id_provided():
    csd_data_set = dict(
        name=NAME,
        sdfhload="CICSTS.IN56.SDFHLOAD",
        state="initial",
        exists=False,
        data_set_organization="NONE",
        unit=MEGABYTES,
        primary=SPACE_PRIMARY_DEFAULT,
        secondary=SPACE_SECONDARY_DEFAULT,
        log="UNDO",
        logstream_id="TEST.DATA.LOG.STREAM"
    )
    idcams_cmd_csd = data_set_utils._build_idcams_define_cmd(csd._get_idcams_cmd_csd(csd_data_set))
    assert idcams_cmd_csd == '''
    DEFINE CLUSTER (NAME(ANSI.TEST.DFHCSD) -
    MEGABYTES(4 1) -
    RECORDSIZE(200 2000) -
    INDEXED -
    KEYS(22 0) -
    FREESPACE(10 10) -
    SHAREOPTIONS(2) -
    REUSE -
    LOG(UNDO)) -
    DATA (NAME(ANSI.TEST.DFHCSD.DATA) -
    CONTROLINTERVALSIZE(8192)) -
    INDEX (NAME(ANSI.TEST.DFHCSD.INDEX))
    '''


@pytest.mark.skipif(sys.version_info.major < 3, reason=PYTHON_LANGUAGE_FEATURES_MESSAGE)
def test_get_idcams_cmd_nonrecoverable():
    csd_data_set = dict(
        name=NAME,
        sdfhload="CICSTS.IN56.SDFHLOAD",
        state="initial",
        exists=False,
        data_set_organization="NONE",
        unit=MEGABYTES,
        primary=SPACE_PRIMARY_DEFAULT,
        secondary=SPACE_SECONDARY_DEFAULT,
        log="NONE"
    )
    idcams_cmd_csd = data_set_utils._build_idcams_define_cmd(csd._get_idcams_cmd_csd(csd_data_set))
    assert idcams_cmd_csd == '''
    DEFINE CLUSTER (NAME(ANSI.TEST.DFHCSD) -
    MEGABYTES(4 1) -
    RECORDSIZE(200 2000) -
    INDEXED -
    KEYS(22 0) -
    FREESPACE(10 10) -
    SHAREOPTIONS(2) -
    REUSE -
    LOG(NONE)) -
    DATA (NAME(ANSI.TEST.DFHCSD.DATA) -
    CONTROLINTERVALSIZE(8192)) -
    INDEX (NAME(ANSI.TEST.DFHCSD.INDEX))
    '''


@pytest.mark.skipif(
    sys.version_info.major < 3, reason=PYTHON_LANGUAGE_FEATURES_MESSAGE
)
def test_get_idcams_cmd_volumes():
    csd_data_set = dict(
        name=NAME,
        sdfhload="CICSTS.IN56.SDFHLOAD",
        state="initial",
        exists=False,
        data_set_organization="NONE",
        unit=MEGABYTES,
        primary=SPACE_PRIMARY_DEFAULT,
        secondary=SPACE_SECONDARY_DEFAULT,
        volumes=["vserv1"]
    )
    idcams_cmd_csd = data_set_utils._build_idcams_define_cmd(csd._get_idcams_cmd_csd(csd_data_set))
    assert idcams_cmd_csd == '''
    DEFINE CLUSTER (NAME(ANSI.TEST.DFHCSD) -
    MEGABYTES(4 1) -
    RECORDSIZE(200 2000) -
    INDEXED -
    KEYS(22 0) -
    FREESPACE(10 10) -
    SHAREOPTIONS(2) -
    REUSE -
    VOLUMES(vserv1)) -
    DATA (NAME(ANSI.TEST.DFHCSD.DATA) -
    CONTROLINTERVALSIZE(8192)) -
    INDEX (NAME(ANSI.TEST.DFHCSD.INDEX))
    '''


@pytest.mark.skipif(
    sys.version_info.major < 3, reason=PYTHON_LANGUAGE_FEATURES_MESSAGE
)
def test_get_idcams_cmd_multiple_volumes():
    csd_data_set = dict(
        name=NAME,
        sdfhload="CICSTS.IN56.SDFHLOAD",
        state="initial",
        exists=False,
        data_set_organization="NONE",
        unit=MEGABYTES,
        primary=SPACE_PRIMARY_DEFAULT,
        secondary=SPACE_SECONDARY_DEFAULT,
        volumes=["vserv1", "vserv2"]
    )
    idcams_cmd_csd = data_set_utils._build_idcams_define_cmd(csd._get_idcams_cmd_csd(csd_data_set))
    assert idcams_cmd_csd == '''
    DEFINE CLUSTER (NAME(ANSI.TEST.DFHCSD) -
    MEGABYTES(4 1) -
    RECORDSIZE(200 2000) -
    INDEXED -
    KEYS(22 0) -
    FREESPACE(10 10) -
    SHAREOPTIONS(2) -
    REUSE -
    VOLUMES(vserv1 vserv2)) -
    DATA (NAME(ANSI.TEST.DFHCSD.DATA) -
    CONTROLINTERVALSIZE(8192)) -
    INDEX (NAME(ANSI.TEST.DFHCSD.INDEX))
    '''


def test_csdup_response():
    setUp()
    csd_input = {
        "exists": False,
        "name": NAME,
        "primary": 5,
        "secondary": 1,
        "unit": "M",
        "state": "initial",
        "vsam": False,
        "sdfhload": "CICSTS.IN56.SDFHLOAD",
    }

    expected_executions = [
        _execution(name=CSDUP_name(), rc=0, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)),
    ]

    csd._execute_dfhcsdup = MagicMock(return_value=MVSCmdResponse(rc=0, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)))
    executions = csd._run_dfhcsdup(csd_input, csd._get_csdup_initilize_cmd())

    assert executions == expected_executions


def test_bad_csdup_response():
    setUp()
    csd_input = {
        "exists": False,
        "name": NAME,
        "primary": 5,
        "secondary": 1,
        "unit": "M",
        "state": "initial",
        "vsam": False,
        "sdfhload": "CICSTS.IN56.SDFHLOAD",
    }

    expected_executions = [
        _execution(name=CSDUP_name(), rc=99, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)),
    ]

    csd._execute_dfhcsdup = MagicMock(return_value=MVSCmdResponse(rc=99, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)))

    try:
        csd._run_dfhcsdup(csd_input, csd._get_csdup_initilize_cmd())
    except MVSExecutionException as e:
        error_message = e.message
        executions = e.executions

        assert error_message == "DFHCSDUP failed with RC 99"
        assert executions == expected_executions
    else:
        assert False


def test_warning_csdup_response():
    setUp()
    csd_input = {
        "exists": False,
        "name": NAME,
        "primary": 5,
        "secondary": 1,
        "unit": "M",
        "state": "initial",
        "vsam": False,
        "sdfhload": "CICSTS.IN56.SDFHLOAD",
    }

    expected_executions = [
        _execution(name=CSDUP_name(), rc=4, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)),
    ]

    csd._execute_dfhcsdup = MagicMock(return_value=MVSCmdResponse(rc=4, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)))

    executions = csd._run_dfhcsdup(csd_input, csd._get_csdup_initilize_cmd())
    assert executions == expected_executions


def test_rc_7_csdup_response():
    setUp()
    csd_input = {
        "exists": False,
        "name": NAME,
        "primary": 5,
        "secondary": 1,
        "unit": "M",
        "state": "initial",
        "vsam": False,
        "sdfhload": "CICSTS.IN56.SDFHLOAD",
    }

    expected_executions = [
        _execution(name=CSDUP_name(), rc=7, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)),
    ]

    csd._execute_dfhcsdup = MagicMock(return_value=MVSCmdResponse(rc=7, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)))

    executions = csd._run_dfhcsdup(csd_input, csd._get_csdup_initilize_cmd())
    assert executions == expected_executions


def test_rc_8_csdup_response():
    setUp()
    csd_input = {
        "exists": False,
        "name": NAME,
        "primary": 5,
        "secondary": 1,
        "unit": "M",
        "state": "initial",
        "vsam": False,
        "sdfhload": "CICSTS.IN56.SDFHLOAD",
    }

    expected_executions = [
        _execution(name=CSDUP_name(), rc=8, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)),
    ]

    csd._execute_dfhcsdup = MagicMock(return_value=MVSCmdResponse(rc=8, stdout=CSDUP_initialize_stdout(NAME), stderr=CSDUP_stderr(NAME)))

    try:
        csd._run_dfhcsdup(csd_input, csd._get_csdup_initilize_cmd())
    except MVSExecutionException as e:
        error_message = e.message
        executions = e.executions

        assert error_message == "DFHCSDUP failed with RC 8"
        assert executions == expected_executions
    else:
        assert False
