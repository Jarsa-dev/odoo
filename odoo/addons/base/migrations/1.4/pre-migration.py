# Copyright 2021 TECMUR S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, installed_version):
    env.cr.execute("""
        ALTER TABLE base_external_dbsource
        ALTER COLUMN connector DROP NOT NULL;
    """)
    _logger.warning('Set company id in stock.move.line')
    env.cr.execute("""
        UPDATE stock_move_line
        SET company_id = 1
        WHERE company_id IS NULL;
    """)
    env.cr.execute("""
        UPDATE quality_check
        SET test_type_id = 1;
    """)
