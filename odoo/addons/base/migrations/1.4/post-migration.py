# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade
from odoo.tools import mute_logger

_logger = logging.getLogger(__name__)

to_remove = [
    'l10n_mx_xml_rate_4_decimals',
    'mt_products',
    'sale_purchase_required_analytic',
    'account_analytic_purchase_flow',
    'mt_css_custom',
    'account_tax_cash_basis_fix_currency_rate_difference',
    'account_followup_report_currency',
    'mt_mrp',
    'security_mt',
    'account_block_unreconcile',
    'MT_custom_report',
]

to_install = [
    'l10n_mx_edi_partner_defaults',
    'account_analytic_tag_assign',
    'l10n_mx_edi_refund',
    'l10n_mx_cash_basis_entries',
    'account_refund_change_account',
    'l10n_mx_avoid_reversal_entry',
    'report_purchase_order_mtnmx',
    'l10n_mx_edi_cancellation_complement',
    'report_account_invoice_mtnmx',
    'l10n_mx_tax_cash_basis',
    'l10n_mx_edi_attachment',
    'l10n_mx_edi_uuid_zip',
    'l10n_mx_edi_vendor_bills',
    'mtnmx',
]

models_to_rename = [
    ('l10n_mx.payment.method', 'l10n_mx_edi.payment.method'),
    ('res.certificate', 'l10n_mx_edi.certificate'),
]

tables_to_rename = [
    ('l10n_mx_payment_method', 'l10n_mx_edi_payment_method'),
    ('res_certificate', 'l10n_mx_edi_certificate'),
]

fields_to_rename = [
    ('account.journal', 'account_journal', 'address_issued_id', 'l10n_mx_address_issued_id'),
    ('account.tax', 'account_tax', 'l10n_mx_edi_factor_type', 'l10n_mx_cfdi_tax_type'),
    ('account.invoice', 'account_invoice', 'l10n_mx_report_name', 'l10n_mx_edi_cfdi_name'),
    ('account.invoice', 'account_invoice', 'account_payment_id', 'l10n_mx_edi_partner_bank_id'),
    ('account.invoice', 'account_invoice', 'l10n_mx_payment_method_id', 'l10n_mx_edi_payment_method_id'),
    ('l10n_mx_edi.certificate', 'l10n_mx_edi_certificate', 'file_cer', 'content'),
    ('l10n_mx_edi.certificate', 'l10n_mx_edi_certificate', 'file_key', 'key'),
    ('res.company', 'res_company', 'l10n_mx_locality', 'l10n_mx_edi_locality'),
    ('res.company', 'res_company', 'l10n_mx_locality', 'l10n_mx_edi_locality'),
    ('res.partner', 'res_partner', 'l10n_mx_payment_method_id', 'l10n_mx_edi_payment_method_id'),
    ('res.partner', 'res_partner', 'l10n_mx_locality', 'l10n_mx_edi_locality'),
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


@mute_logger('odoo.addons.base.models.ir_attachment')
def recover_attachments(env):
    att_obj = env['ir.attachment']
    attachments = att_obj.search([
        ('res_model', '=', 'account.invoice'),
        ('name', 'ilike', '%.xml'),
        ('index_content', '!=', False)])
    for attachment in attachments:
        if not attachment.store_fname:
            attachment.unlink()
            continue
        file = att_obj._file_read(attachment.store_fname)
        if isinstance(file, str):
            full_path = att_obj._full_path(attachment.store_fname)
            file = open(full_path, 'w+')
            file.write(attachment.index_content)
            file.close()


@openupgrade.migrate()
def migrate(env, installed_version):
    recover_attachments(env)
    openupgrade.rename_models(env.cr, models_to_rename)
    openupgrade.rename_tables(env.cr, tables_to_rename)
    openupgrade.rename_fields(env, fields_to_rename)
    env.cr.execute(
        'ALTER TABLE account_journal DROP CONSTRAINT '
        'account_journal_l10n_mx_edi_payment_method_id_fkey')
    env.cr.execute(
        'ALTER TABLE base_automation DROP CONSTRAINT '
        'base_automation_action_server_id_fkey')
    env.cr.execute(
        'ALTER TABLE ir_cron DROP CONSTRAINT '
        'ir_cron_ir_actions_server_id_fkey')
    rename_modules(env, 'mt_custom_views', 'mtnmx')
    rename_modules(env, 'l10n_mx_base', 'l10n_mx_edi')
    rename_modules(env, 'mt_invoice_report', 'report_account_invoice_mtnmx')
    rename_modules(env, 'report_account_move_libros_contab', 'report_account_move_mtnmx')
    env['ir.module.module'].update_list()
    modules_to_install = env['ir.module.module'].search([
        ('name', 'in', to_install)])
    modules_to_install.button_install()
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
