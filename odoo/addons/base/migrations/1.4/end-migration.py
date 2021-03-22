# Copyright 2019 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, installed_version):
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '13.0.1.3'
        WHERE name = 'base';
    """)
    env.cr.execute("""
        ALTER TABLE base_external_dbsource
        ALTER COLUMN connector SET NOT NULL;
    """)
    os.system('say el script de migración ha concluido')
