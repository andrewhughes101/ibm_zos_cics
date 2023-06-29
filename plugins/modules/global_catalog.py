#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) Copyright IBM Corp. 2020,2023
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: global_catalog
short_description: Create and initialize CICS® global catalog.
description: Create, update, and remove a CICS® global catalog dataset to be used by a CICS® region, achieved by running the IDCAMS and DFHRMUTL programs.
author: Andrew Twydell (@AndrewTwydell)
version_added: 1.1.0-beta.1
options:
  space_primary:
    description: Specifies the size of the global catalog dataset. Note, this is just the value; the unit is specified with space_type.
    type: int
    required: false
    default: 5
  space_type:
    description: Specifies the unit to be used for the global catalog size. Note, this is just the unit; the value is specified with space_primary.
    required: false
    type: str
    choices:
      - M
      - K
      - REC
      - CYL
      - TRK
    default: M
  location:
    description: The name of the dataset to be used as the global catalog dataset.
    type: str
    required: true
  sdfhload:
    description: The location of SDFHLOAD for the CICS install to be used to create the global catalog.
    type: str
    required: true
  state:
    description: The state the catalog will end up in after the task has run.
    choices:
      - "initial"
      - "absent"
      - "cold"
      - "warm"
    required: true
    type: str
'''


EXAMPLES = r"""
- name: Initialize a global catalog
  ibm.ibm_zos_cics.global_catalog:
    location: "CICS.INSTALL.REG01.DFHGCD"
    sdfhload: "CTS560.CICS730.SDFHLOAD"
    state: "initial"

- name: Initialize a large catalog
  ibm.ibm_zos_cics.global_catalog:
    location: "CICS.INSTALL.REG01.DFHGCD"
    sdfhload: "CTS560.CICS730.SDFHLOAD"
    space_primary: 100
    space_type: "M"
    state: "initial"

- name: Set AUTO_START_OVERRIDE record to be AUTOASIS
  ibm.ibm_zos_cics.global_catalog:
    location: "CICS.INSTALL.REG01.DFHGCD"
    sdfhload: "CTS560.CICS730.SDFHLOAD"
    state: "warm"

- name: Set AUTO_START_OVERRIDE record to be AUTOCOLD
  ibm.ibm_zos_cics.global_catalog:
    location: "CICS.INSTALL.REG01.DFHGCD"
    sdfhload: "CTS560.CICS730.SDFHLOAD"
    state: "cold"

- name: Delete global catalog
  ibm.ibm_zos_cics.global_catalog:
    location: "CICS.INSTALL.REG01.DFHGCD"
    sdfhload: "CTS560.CICS730.SDFHLOAD"
    state: "absent"
"""


RETURN = r"""
changed:
  description: True if the state was changed, otherwise False.
  returned: always
  type: bool
failed:
  description: True if the query job failed, otherwise False.
  returned: always
  type: bool
is_zos:
  description: True if the target environment is z/OS
  returned: always
  type: bool
starting_catalog:
  description:
    - The state of the global catalog before the task
  returned: success
  type: dict
  contains:
    autostart_override:
      description: The current autostart override record
      returned: success
      type: str
    name:
      description: The name of the global catalog dataset
      returned: success
      type: str
    nextstart:
      description: The next start type listed in the catalog
      returned: success
      type: str
    sdfhload:
      description: The name of the sdfhload
      returned: success
      type: str
    state:
      description: The specified target state for the catalog
      returned: success
      type: str
    exists:
      description: True if the global catalog dataset exists
      type: bool
      returned: success
    vsam:
      description: True if the global catalog dataset is a VSAM
      type: bool
      returned: success
    size:
      description: Size parameters of the catalog dataset
      returned: success
      type: dict
      contains:
        primary:
          description: The primary size allocated for the catalog
          type: int
          returned: success
        secondary:
          description: The secondary size allocated for the catalog
          type: int
          returned: success
        unit:
          description: The size unit used for the catalog
          type: str
          returned: success
end_catalog:
  description: The state of the global catalog at the end of the task.
  returned: success
  type: dict
  contains:
    autostart_override:
      description: The current autostart override record
      returned: success
      type: str
    name:
      description: The name of the global catalog dataset
      returned: success
      type: str
    nextstart:
      description: The next start type listed in the catalog
      returned: success
      type: str
    sdfhload:
      description: The name of the sdfhload
      returned: success
      type: str
    state:
      description: The specified target state for the catalog
      returned: success
      type: str
    exists:
      description: True if the global catalog dataset exists
      type: bool
      returned: success
    vsam:
      description: True if the global catalog dataset is a VSAM
      type: bool
      returned: success
    size:
      description: Size parameters of the catalog dataset
      returned: success
      type: dict
      contains:
        primary:
          description: The primary size allocated for the catalog
          type: int
          returned: success
        secondary:
          description: The secondary size allocated for the catalog
          type: int
          returned: success
        unit:
          description: The size unit used for the catalog
          type: str
          returned: success
result:
  description: The result of the CICS programs run during the module execution.
  type: dict
  returned: success
  contains:
    msg:
      description: The string message returned by the CICS program.
      type: str
      returned: always
    rc:
      description: The return code of the CICS program.
      type: int
      returned: always
    success:
      description: True if the CICS program was successful
      type: bool
      returned: always
"""


from typing import Dict
from ansible.module_utils.basic import AnsibleModule
import traceback

DDStatement = None
ZOS_CORE_IMP_ERR = None
try:
    from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import BetterArgParser
except ImportError:
    ZOS_CORE_IMP_ERR = traceback.format_exc()

ZOS_CICS_IMP_ERR = None
try:
    from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils.dataset_utils import (
        GlobalCatalog, CatalogSize, get_idcams_create_cmd)
    from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils.listds import run_listds
    from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils.idcams import run_idcams
    from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils.dfhrmutl import run_dfhrmutl
except ImportError:
    ZOS_CICS_IMP_ERR = traceback.format_exc()


CATALOG_GCD_ALIAS = "location"
CATALOG_STEPLIB_ALIAS = "sdfhload"
CATALOG_TARGET_STATE_ALIAS = "state"

CATALOG_PRIMARY_SPACE_VALUE_ALIAS = "space_primary"
CATALOG_PRIMARY_SPACE_VALUE_DEFAULT = 5

CATALOG_PRIMARY_SPACE_UNIT_ALIAS = "space_type"
CATALOG_PRIMARY_SPACE_UNIT_DEFAULT = "M"
CATALOG_SPACE_UNIT_OPTIONS = ["K", "M", "REC", "CYL", "TRK"]

CATALOG_SECONDARY_SPACE_VALUE_DEFAULT = 1

CATALOG_RECORD_COUNT_DEFAULT = 4089
CATALOG_RECORD_SIZE_DEFAULT = 32760
CATALOG_CONTROL_INTERVAL_SIZE_DEFAULT = 32768

CATALOG_TARGET_STATE_OPTIONS = ['absent', 'initial', 'cold', 'warm']

AUTO_START_WARM = "AUTOASIS"
AUTO_START_COLD = "AUTOCOLD"
AUTO_START_INIT = "AUTOINIT"

NEXT_START_EMERGENCY = "EMERGENCY"
NEXT_START_WARM = "WARM"
NEXT_START_COLD = "COLD"
NEXT_START_UNKNOWN = "UNKNOWN"


class AnsibleGlobalCatalogModule(object):

    def __init__(self):
        self._module = AnsibleModule(
            argument_spec=self.init_argument_spec(),
        )
        self.result = {}
        self.result['changed'] = False
        self.result['failed'] = False
        self.result['executions'] = []
        self.executions = []
        self.validate_parameters()

    def _fail(self, msg):  # type: (str) -> None
        self.result['failed'] = True
        self.result['executions'] = self.executions
        self._module.fail_json(msg=msg, **self.result)

    def _exit(self):
        self.result['executions'] = self.executions
        self._module.exit_json(**self.result)

    def init_argument_spec(self):  # type: () -> Dict
        return {
            CATALOG_PRIMARY_SPACE_VALUE_ALIAS: {
                'required': False,
                'type': 'int',
                'default': CATALOG_PRIMARY_SPACE_VALUE_DEFAULT,
            },
            CATALOG_PRIMARY_SPACE_UNIT_ALIAS: {
                'required': False,
                'type': 'str',
                'choices': CATALOG_SPACE_UNIT_OPTIONS,
                'default': CATALOG_PRIMARY_SPACE_UNIT_DEFAULT,
            },
            CATALOG_GCD_ALIAS: {
                'required': True,
                'type': 'str',
            },
            CATALOG_STEPLIB_ALIAS: {
                'required': True,
                'type': 'str',
            },
            CATALOG_TARGET_STATE_ALIAS: {
                'required': True,
                'type': 'str',
                'choices': CATALOG_TARGET_STATE_OPTIONS,
            },
        }

    def validate_parameters(self):
        arg_defs = {
            CATALOG_PRIMARY_SPACE_VALUE_ALIAS: {
                "arg_type": 'int',
                "default": CATALOG_PRIMARY_SPACE_VALUE_DEFAULT,
            },
            CATALOG_PRIMARY_SPACE_UNIT_ALIAS: {
                "arg_type": 'str',
                "choices": CATALOG_SPACE_UNIT_OPTIONS,
                "default": CATALOG_PRIMARY_SPACE_UNIT_DEFAULT,
            },
            CATALOG_GCD_ALIAS: {
                "arg_type": 'data_set_base',
                "required": True,
            },
            CATALOG_STEPLIB_ALIAS: {
                "arg_type": 'data_set_base',
                "required": True,
            },
            CATALOG_TARGET_STATE_ALIAS: {
                "arg_type": 'str',
                "choices": CATALOG_TARGET_STATE_OPTIONS,
                "required": True,
            },
        }
        result = BetterArgParser(arg_defs).parse_args({
            "space_primary": self._module.params.get(CATALOG_PRIMARY_SPACE_VALUE_ALIAS),
            "space_type": self._module.params.get(CATALOG_PRIMARY_SPACE_UNIT_ALIAS),
            "location": self._module.params.get(CATALOG_GCD_ALIAS).upper(),
            "sdfhload": self._module.params.get(CATALOG_STEPLIB_ALIAS).upper(),
            "state": self._module.params.get(CATALOG_TARGET_STATE_ALIAS)
        })
        self.starting_catalog = GlobalCatalog(
            size=CatalogSize(
                result.get('space_type'),
                result.get('space_primary'),
                CATALOG_SECONDARY_SPACE_VALUE_DEFAULT,
                CATALOG_RECORD_COUNT_DEFAULT,
                CATALOG_RECORD_SIZE_DEFAULT,
                CATALOG_CONTROL_INTERVAL_SIZE_DEFAULT),
            name=result.get('location'),
            sdfhload=result.get('sdfhload'),
            state=result.get('state'),
            autostart_override="",
            nextstart="",
            exists=False,
            vsam=False)
        self.end_catalog = self.starting_catalog

    def create_global_catalog_dataset(self):
        create_cmd = get_idcams_create_cmd(self.starting_catalog)

        idcams_executions = run_idcams(
            cmd=create_cmd,
            name="Create global catalog dataset",
            location=self.starting_catalog.name,
            delete=False)
        self.executions.append([element.to_dict()
                                for element in idcams_executions])

        self.result['changed'] = True

    def delete_global_catalog(self):
        if not self.starting_catalog.exists:
            self.result['end_catalog'] = {
                "exists": self.starting_catalog.exists,
                "autostart_override": self.starting_catalog.autostart_override,
                "next_start": self.starting_catalog.nextstart,
            }
            self._exit()

        delete_cmd = '''
        DELETE {0}
        '''.format(self.starting_catalog.name)

        idcams_executions = run_idcams(
            cmd=delete_cmd,
            name="Removing global catalog dataset",
            location=self.starting_catalog.name,
            delete=True)
        self.executions.append([element.to_dict()
                                for element in idcams_executions])
        self.result['changed'] = True

    def init_global_catalog(self):
        if self.starting_catalog.exists and self.starting_catalog.autostart_override == AUTO_START_INIT:
            self.result['end_catalog'] = {
                "exists": self.starting_catalog.exists,
                "autostart_override": self.starting_catalog.autostart_override,
                "next_start": self.starting_catalog.nextstart,
            }
            self._exit()

        if not self.starting_catalog.exists:
            self.create_global_catalog_dataset()

        dfhrmutl_executions = run_dfhrmutl(
            self.starting_catalog.name,
            self.starting_catalog.sdfhload,
            cmd="SET_AUTO_START=AUTOINIT")
        self.result['changed'] = True
        self.executions.append([element.to_dict()
                                for element in dfhrmutl_executions])

    def warm_global_catalog(self):
        if not self.starting_catalog.exists:
            self._fail(
                "Dataset {0} does not exist.".format(
                    self.starting_catalog.name))

        if self.starting_catalog.autostart_override == AUTO_START_WARM:
            self.result['end_catalog'] = {
                "exists": self.starting_catalog.exists,
                "autostart_override": self.starting_catalog.autostart_override,
                "next_start": self.starting_catalog.nextstart,
            }
            self._exit()

        if (
            self.starting_catalog.autostart_override == AUTO_START_INIT and
            self.starting_catalog.nextstart == NEXT_START_UNKNOWN
        ):
            self._fail(
                "Unused Catalog - it must be used by CICS before doing a warm start")

        dfhrmutl_executions = run_dfhrmutl(
            self.starting_catalog.name,
            self.starting_catalog.sdfhload,
            cmd="SET_AUTO_START=AUTOASIS")
        self.result['changed'] = True
        self.executions.append([element.to_dict()
                                for element in dfhrmutl_executions])

    def cold_global_catalog(self):
        if not self.starting_catalog.exists:
            self._fail(
                "Dataset {0} does not exist.".format(
                    self.starting_catalog.name))

        if self.starting_catalog.autostart_override == AUTO_START_COLD:
            self.result['end_catalog'] = {
                "exists": self.starting_catalog.exists,
                "autostart_override": self.starting_catalog.autostart_override,
                "next_start": self.starting_catalog.nextstart,
            }
            self._exit()

        if (
            self.starting_catalog.autostart_override == AUTO_START_INIT and
            self.starting_catalog.nextstart == NEXT_START_UNKNOWN
        ):
            self._fail(
                "Unused Catalog - it must be used by CICS before doing a cold start")

        dfhrmutl_executions = run_dfhrmutl(
            self.starting_catalog.name,
            self.starting_catalog.sdfhload,
            cmd="SET_AUTO_START=AUTOCOLD")
        self.result['changed'] = True
        self.executions.append([element.to_dict()
                                for element in dfhrmutl_executions])

    def invalid_target_state(self):  # type: () -> None
        self._fail("{0} is not a valid target state".format(
            self.global_catalog.state))

    def get_target_method(self, target):
        return {
            'absent': self.delete_global_catalog,
            'initial': self.init_global_catalog,
            'cold': self.cold_global_catalog,
            'warm': self.warm_global_catalog,
        }.get(target, self.invalid_target_state)

    def update_catalog(self, catalog):
        listds_executions, ds_status = run_listds(catalog.name)

        catalog.exists = ds_status['exists']
        catalog.vsam = ds_status['vsam']

        self.executions.append([element.to_dict()
                                for element in listds_executions])

        if catalog.exists and catalog.vsam:
            dfhrmutl_executions, catalog_status = run_dfhrmutl(
                catalog.name, catalog.sdfhload)

            catalog.autostart_override = catalog_status['autostart_override']
            catalog.nextstart = catalog_status['next_start']

            self.executions.append([element.to_dict()
                                    for element in dfhrmutl_executions])
        else:
            catalog.autostart_override = ""
            catalog.nextstart = ""
        return catalog

    def main(self):
        self.starting_catalog = self.update_catalog(self.starting_catalog)

        self.result['start_catalog'] = {
            "exists": self.starting_catalog.exists,
            "autostart_override": self.starting_catalog.autostart_override,
            "next_start": self.starting_catalog.nextstart,
        }

        if self.starting_catalog.nextstart and self.starting_catalog.nextstart.upper(
        ) == NEXT_START_EMERGENCY:
            self._fail("Next start type is {0}, potential dataloss prevented".format(
                NEXT_START_EMERGENCY))

        self.get_target_method(
            self.starting_catalog.state)()

        self.end_catalog = self.update_catalog(self.end_catalog)

        self.result['end_catalog'] = {
            "exists": self.end_catalog.exists,
            "autostart_override": self.end_catalog.autostart_override,
            "next_start": self.end_catalog.nextstart,
        }
        self._exit()


def main():
    AnsibleGlobalCatalogModule().main()


if __name__ == '__main__':
    main()
