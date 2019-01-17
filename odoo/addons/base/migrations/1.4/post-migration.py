# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

to_remove = [
    'custom_views_jarsa',
    'security_jarsa',
    'project_task_auto_assign',
    'studio_customization',
    'website_style',
    'website_menu_megamenu',
    'website_analytics_hotjar',
    'theme_common',
    'l10n_mx_portal',
    'helpdesk_status',
    'helpdesk_signature_remover',
    'website_animate',
    'website_seo_redirection',
    'l10n_mx_edi_vendor_bills',
    'mail_tracking_mass_mailing',
    'sale_contract_automated_mail',
    'invoice_custom_report_jarsa',
    'theme_graphene',
    'helpdesk_task',
]

to_install = [
    'helpdesk_sale_timesheet',
    'l10n_mx_edi_partner_defaults',
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

records_to_remove = [
    'helpdesk_close_tickets.hr_timesheet_project_task_jarsa',
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
    openupgrade.rename_models(env.cr, models_to_rename)
    openupgrade.rename_tables(env.cr, tables_to_rename)
    openupgrade.rename_fields(env, fields_to_rename)
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    env.cr.execute(
        'ALTER TABLE account_journal DROP CONSTRAINT '
        'account_journal_l10n_mx_edi_payment_method_id_fkey')
    modules_to_install = env['ir.module.module'].search([
        ('name', 'in', to_install)])
    modules_to_install.button_install()
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
    rename_modules(env, 'helpdesk_open_ticket', 'helpdesk_task_automation')
    rename_modules(env, 'helpdesk_close_tickets', 'helpdesk_task_automation')
    rename_modules(env, 'helpdesk_task', 'helpdesk_task_automation')
    rename_modules(env, 'helpdesk_merge_tickets', 'helpdesk_ticket_merge')
    rename_modules(env, 'crm_new_lead', 'helpdesk_ticket_to_lead')
    rename_modules(env, 'l10n_mx_base', 'l10n_mx_edi')
