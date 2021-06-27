# Copyright 2021 TECMUR S.A. de C.V.
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
    env.cr.execute("""
        UPDATE ir_ui_view
        SET active = True
        WHERE
        name in (
        'stock.picking.view.form.custom.date',
        'stock.picking.by.partner.tecmur.form',
        'stock.picking.tecmur.form')
        AND
        model = 'stock.picking'
        AND
        inherit_id = 554;
    """)
    env.cr.execute("""
        UPDATE ir_ui_view
        SET active = True
        WHERE
        name in (
        'mrp.production.by.lot.inherit.tecmur.form'
        )
        AND
        model = 'mrp.production'
        AND
        inherit_id = 1270;
    """)
    # env.cr.execute("""
    #     UPDATE account_move
    #     SET authorized = True
    #     WHERE name
    #     IN
    #     (
    #     SELECT move_name
    #     FROM account_invoice
    #     WHERE authorized = True
    #     AND
    #     type = 'in_invoice'
    #     );
    # """)
    # env.cr.execute("""
    #     UPDATE account_move
    #     SET authorized = False
    #     WHERE authorized IS NULL
    #     AND
    #     type = 'in_invoice';
    # """)
    os.system('say el script de migración ha concluido')
