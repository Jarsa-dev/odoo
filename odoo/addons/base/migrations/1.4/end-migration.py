# Copyright 2022 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from openupgradelib import openupgrade
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


to_remove = [
    "account_invoice_automatic_landed_costs",
    "purchase_invoice_line_zero",
    "purchase_request_notify_tecmur",
    "l10n_mx_edi_partner_defaults",
    "l10n_mx_edi_uuid",
    "mrp_production_split",
    "product_template_tags",
    "stock_scrap_tier_validation",
]


# List of strings with XML ID.
records_to_remove = [
]


def _process_stock_valuation_layer(env):
    _logger.warning("Adding lot_id column to stock_valuation_layer")
    env.cr.execute("""
        UPDATE stock_valuation_layer AS svl
        SET lot_id = to_update.lot_id
        FROM (
            WITH svl_count AS (SELECT
                stock_valuation_layer_id,
                STRING_AGG(DISTINCT stock_production_lot_id::text, ',') AS lots,
                COUNT(*) AS cant
            FROM stock_production_lot_stock_valuation_layer_rel
            GROUP BY stock_valuation_layer_id)
            SELECT
                stock_valuation_layer_id,
                lots::int AS lot_id
            FROM svl_count
            WHERE cant < 2
        ) AS to_update
        WHERE svl.id = to_update.stock_valuation_layer_id
    """)
    env.cr.execute("""
        SELECT
            id,
            create_uid,
            create_date,
            write_uid,
            write_date,
            company_id,
            product_id,
            COALESCE(quantity, 0) AS quantity,
            COALESCE(unit_cost, 0) AS unit_cost,
            COALESCE(value, 0) AS value,
            COALESCE(remaining_qty, 0) AS remaining_qty,
            description,
            stock_valuation_layer_id,
            stock_move_id,
            account_move_id,
            COALESCE(remaining_value, 0) AS remaining_value,
            stock_landed_cost_id,
            categ_id,
            account_move_line_id,
            COALESCE(price_diff_value, 0) AS price_diff_value
        FROM stock_valuation_layer WHERE id IN(
            WITH svl_count AS (SELECT
                stock_valuation_layer_id,
                STRING_AGG(DISTINCT stock_production_lot_id::text, ',') AS lots,
                COUNT(*) AS cant
            FROM stock_production_lot_stock_valuation_layer_rel
            GROUP BY stock_valuation_layer_id)
            SELECT
                stock_valuation_layer_id AS id
            FROM svl_count
            WHERE cant > 2
        )
    """)
    svl_dict = env.cr.dictfetchall()
    _logger.warning("Starting reprocessing of stock_valuation_layer: %s", len(svl_dict))
    count = 0
    for svl in svl_dict:
        count += 1
        if count % 1000 == 0:
            _logger.warning("Processed %s of %s stock_valuation_layer records", count, len(svl_dict))
        if svl.get("remaining_value", 0.0) > 0.0:
            _logger.warning("Skipping stock_valuation_layer %s with remaining_value > 0.0", svl.get("id", False))
            continue
        env.cr.execute("SELECT quantity, lot_id FROM stock_move_line WHERE move_id = %(stock_move_id)s", svl)
        sml_dict = env.cr.dictfetchall()
        unit_cost = svl.get("value", 0.0) / 1 if not svl.get("quantity", 1.0) else svl.get("quantity")
        first = False
        for sml in sml_dict:
            if not first:
                env.cr.execute("UPDATE stock_valuation_layer SET lot_id = %(lot_id)s, unit_cost = %(unit_cost)s, value = %(value)s, quantity = %(quantity)s WHERE id = %(id)s", {
                    "lot_id": sml.get("lot_id", False),
                    "id": svl.get("id", False),
                    "unit_cost": unit_cost,
                    "value": sml.get("quantity", 0) * unit_cost,
                    "quantity": sml.get("quantity", 0),
                })
                first = True
                continue
            env.cr.execute("""
                INSERT INTO stock_valuation_layer (create_uid, create_date, write_uid, write_date, company_id, product_id, quantity, unit_cost, value, remaining_qty, description, stock_valuation_layer_id, stock_move_id, account_move_id, remaining_value, stock_landed_cost_id, categ_id, account_move_line_id, price_diff_value, lot_id)
                VALUES (
                    %(create_uid)s, %(create_date)s, %(write_uid)s, %(write_date)s, %(company_id)s, %(product_id)s, %(quantity)s, %(unit_cost)s, %(value)s, %(remaining_qty)s, %(description)s, %(stock_valuation_layer_id)s, %(stock_move_id)s, %(account_move_id)s, %(remaining_value)s, %(stock_landed_cost_id)s, %(categ_id)s, %(account_move_line_id)s, %(price_diff_value)s, %(lot_id)s
                )
            """, {
                "create_uid": svl.get("create_uid", False),
                "create_date": svl.get("create_date", False),
                "write_uid": svl.get("write_uid", False),
                "write_date": svl.get("write_date", False),
                "company_id": svl.get("company_id", False),
                "product_id": svl.get("product_id", False),
                "quantity": sml.get("quantity", 0),
                "unit_cost": unit_cost,
                "value": sml.get("quantity", 0) * unit_cost,
                "remaining_qty": svl.get("remaining_qty", 0),
                "description": svl.get("description", False),
                "stock_valuation_layer_id": svl.get("stock_valuation_layer_id", False),
                "stock_move_id": svl.get("stock_move_id", False),
                "account_move_id": svl.get("account_move_id", False),
                "remaining_value": svl.get("remaining_value", 0.0),
                "stock_landed_cost_id": svl.get("stock_landed_cost_id", False),
                "categ_id": svl.get("categ_id", False),
                "account_move_line_id": svl.get("account_move_line_id", False),
                "price_diff_value": svl.get("price_diff_value", 0.0),
                "lot_id": sml.get("lot_id", False),
            })

@openupgrade.migrate()
def migrate(env, installed_version):
    if records_to_remove:
        _logger.warning('Delete records from XML ID')
        openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    if to_remove:
        _logger.warning('Uninstalling not required modules')
        modules_to_remove = env['ir.module.module'].search([
            ('name', 'in', to_remove)])
        modules_to_remove += modules_to_remove.downstream_dependencies()
        modules_to_remove.module_uninstall()
        modules_to_remove.unlink()
    _process_stock_valuation_layer(env)
    env["purchase.request"].search([]).write({"is_name_editable": False})
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '15.0.1.4'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
    _logger.warning('The migration has finished')
