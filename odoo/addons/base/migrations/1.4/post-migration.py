# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# List of modules to install
to_install = [
    'l10n_mx_edi_reconciliation_uuid',
    'l10n_mx_edi_partner_defaults',
]

# List of modules to remove (uninstall)
to_remove = [
    # 'stock_disable_force_availability_button',
    # 'auto_backup',
    # 'account_multicurrency_revaluation',
    # 'account_reversal',
    # 'account_move_line_currency_compute',
    # 'account_tax_cash_basis_reference',
    # 'account_invoice_fix_number',
    # 'web_widget_many2many_tags_multi_selection',
    # 'account_tax_cash_basis_fix_currency_rate_difference',
    # 'siti_custom_css',
    # 'purchase_line_invoice_line_zero',
    # 'res_partner_statement',
    # 'account_move_line_stock_info',
    # 'stock_kardex',
    # 'res_currency_rate_custom_decimals',
    # 'account_partner_currency_statement',
    # 'base_partner_merge',
    # 'account_reconciliation_uuid',
]

# List of modules to remove all views.
modules_remove_views = [
    'l10n_mx_base',
]

# List of strings with XML ID.
records_to_remove = []

# List of tuples with the following format
# ('old.model.name', 'new.model.name'),
models_to_rename = [
    # ('l10n_mx.payment.method', 'l10n_mx_edi.payment.method'),
    # ('l10n_mx_edi.product.sat.code', 'product.unspsc.code'),
]

# List of tuples with the following format
# ('old_table_name', 'new_table_name'),
tables_to_rename = [
    # ('l10n_mx_payment_method', 'l10n_mx_edi_payment_method'),
    # ('l10n_mx_edi_product_sat_code', 'product_unspsc_code'),
]

# List of tuples with the following format
# ('model.name', 'table_name', 'old_field', 'new_field'),
fields_to_rename = [
    ('res.partner', 'res_partner', 'l10n_mx_payment_method_id', 'l10n_mx_edi_payment_method_id'),
    # ('product.template', 'product_template', 'l10n_mx_edi_sat_code_id', 'unspsc_code_id'),
    # ('uom.uom', 'uom_uom', 'l10n_mx_edi_sat_code_id', 'unspsc_code_id'),
]

# List of tuples with the follwing format
# ('old_module_name', 'new_module_name'),
modules_to_rename = [
    ('l10n_mx_edi_third_party_payment_complement', 'l10n_mx_edi_extended'),
    ('stock_picking_report', 'report_stock_picking_sitibt'),
    ('l10n_mx_landing', 'l10n_mx_edi_landing'),
    ('saleorder_custom_report', 'report_sale_order_sitibt'),
    ('l10n_mx_base', 'l10n_mx_edi'),
    ('account_invoice_custom_refund', 'l10n_mx_edi_product_refund_accounts'),
    ('account_move_report', 'report_account_move_sitibt'),
    ('invoice_custom_report', 'report_account_invoice_sitibt'),
    ('security_siti', 'sitibt'),
    ('siti_custom_view_noeditable', 'sitibt'),
    ('siti_customs_view', 'sitibt'),
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


def remove_module_views(env, module_list):
    def recursive_inherit_ids(records):
        env.cr.execute("""
            SELECT inherit_id AS id
            FROM ir_ui_view
            WHERE id IN %(ids)s AND inherit_id IS NOT NULL;
        """, {'ids': tuple(records.mapped('res_id'))})
        res = env.cr.fetchall()
        view_ids = [x[0] for x in res]
        new_records = env['ir.model.data'].search([
            ('model', '=', 'ir.ui.view'),
            ('res_id', 'in', view_ids)
        ])
        new_records |= records
        if len(new_records) == len(records):
            return records
        return recursive_inherit_ids(new_records)
    recs = env['ir.model.data'].search([
        ('model', '=', 'ir.ui.view'),
        ('module', 'in', module_list),
    ])
    records = recursive_inherit_ids(recs)
    return records.mapped('complete_name')


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Delete records from XML ID')
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    openupgrade.delete_records_safely_by_xml_id(
        env, remove_module_views(env, modules_remove_views))
    for module in modules_to_rename:
        rename_modules(env, module[0], module[1])
    openupgrade.rename_models(env.cr, models_to_rename)
    openupgrade.rename_tables(env.cr, tables_to_rename)
    openupgrade.rename_fields(env, fields_to_rename)
    env['ir.module.module'].update_list()
    _logger.warning('Installing new modules')
    modules_to_install = env['ir.module.module'].search([
        ('name', 'in', to_install)])
    modules_to_install.button_install()
    _logger.warning('Uninstalling not required modules')
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
    modules_to_remove.unlink()
