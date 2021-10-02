# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# List of modules to install
to_install = [
    'stock_free_quantity',
    'l10n_mx_edi_report',
    'l10n_mx_avoid_reversal_entry',
    '10n_mx_edi_account_followup',
    'purchase_order_secondary_unit',
    'mrp_request',
    'mrp_request_produce_location',
    'stock_secondary_unit',
]

# List of modules to remove (uninstall)
to_remove = [
    'account_currency_rate_difference_reference',
    'account_fiscal_year_closing',
    'account_invoice_fix_number',
    'account_skip_exchange_reversal',
    'account_tax_cash_basis_reference',
    'account_xunnel',
    'l10n_mx_edi_addendas',
    'l10n_mx_edi_bank',
    'l10n_mx_edi_vendor_validation',
    'mrp_auto_assign',
    'stock_kardex_report',
    'stock_account_valuation_report',
    'res_currency_rate_custom_decimals',
    'stock_mts_mto_mrp',
    'mrp_production_limit',
    'stock_automatic_lot',
    'sale_order_secondary_unit',
    'sale_stock_secondary_unit',
]

# List of strings with XML ID.
records_to_remove = [
    'stock_uom_equivalence.product_template_stock_uom_equivalence_form_view',
    'stock_uom_equivalence.product_normal_stock_uom_equivalence_form_view',
    'stock_uom_equivalence.view_stock_product_tree2_stock_uom_equivalence',
    'stock_uom_equivalence.view_move_picking_form_stock_uom_equivalence',
    'stock_uom_equivalence.view_stock_move_operations_stock_uom_equivalence',
    'stock_uom_equivalence.view_stock_move_line_operation_tree_stock_uom_equivalence',
    'stock_uom_equivalence.view_picking_form_stock_uom_equivalence',
    'stock_uom_equivalence.view_stock_quant_tree_stock_uom_equivalence',
    'stock_uom_equivalence.view_stock_quant_form_stock_uom_equivalence',
    'stock_uom_equivalence.report_delivery_document_stock_equivalence',
]

# List of tuples with the following format
# ('old.model.name', 'new.model.name'),
models_to_rename = []

# List of tuples with the following format
# ('old_table_name', 'new_table_name'),
tables_to_rename = []

# List of tuples with the following format
# ('model.name', 'table_name', 'old_field', 'new_field'),
fields_to_rename = []

# List of tuples with the follwing format
# ('old_module_name', 'new_module_name'),
modules_to_rename = [
    ('mrp_production_request', 'mrp_request'),
    ('mrp_production_request_produce_location', 'mrp_request_produce_location'),
    ('account_aged_partner_balance_by_currency', 'account_aged_by_currency_report'),
    ('bo_import_direct_drive_sheet', 'google_spreadsheet_import'),
]


def rename_modules(env, old, new):
    env['ir.module.module'].update_list()
    _logger.warning(
        'Rename module %s -> %s' % (old, new))
    module = env['ir.module.module'].search(
        [('name', '=', new)])
    old_module = env['ir.module.module'].search(
        [('name', '=', old)])
    module.invalidate_cache()
    if module and old_module:
        env.cr.execute(
            "DELETE FROM ir_model_data WHERE name = 'module_%s'" % new)
        env.cr.execute(
            'DELETE FROM ir_module_module WHERE id = %s' % module.id)
        openupgrade.update_module_names(env.cr, [(old, new)])


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Delete records from XML ID')
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    openupgrade.rename_models(env.cr, models_to_rename)
    openupgrade.rename_tables(env.cr, tables_to_rename)
    openupgrade.rename_fields(env, fields_to_rename)
    for module in modules_to_rename:
        rename_modules(env, module[0], module[1])
    env['ir.module.module'].update_list()
    modules_to_install = env['ir.module.module'].search([
        ('name', 'in', to_install)])
    modules_to_install.button_install()
    _logger.warning('Uninstall modules not required')
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
    modules_to_remove.unlink()
