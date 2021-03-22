# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Removing bank accounts with no partner')
    env.cr.execute("""
        ALTER TABLE base_external_dbsource
        ALTER COLUMN connector DROP NOT NULL;
    """)
