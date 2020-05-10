# Copyright 2019 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from openupgradelib import openupgrade
from lxml.etree import XMLSyntaxError

_logger = logging.getLogger(__name__)


records_to_remove = []


@openupgrade.migrate()
def migrate(env, installed_version):
    # openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    _logger.warning('Reset base module to version 1.3')
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '12.0.1.3'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
