# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from datetime import date

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


to_remove = [
    'stock_disable_force_availability_button',
    'auto_backup',
    'account_multicurrency_revaluation',
    'account_reversal',
    'account_move_line_currency_compute',
    'account_tax_cash_basis_reference',
    'account_invoice_fix_number',
    'web_widget_many2many_tags_multi_selection',
    'account_tax_cash_basis_fix_currency_rate_difference',
    'siti_custom_css',
    'purchase_line_invoice_line_zero',
    'res_partner_statement',
    'account_move_line_stock_info',
    'stock_kardex',
    'res_currency_rate_custom_decimals',
    'account_partner_currency_statement',
    'base_partner_merge',
    'account_reconciliation_uuid',
]


# List of strings with XML ID.
records_to_remove = []


def fix_l10n_mx_cfdi_tax_type(env):
    values_to_fix = {
        'rate': 'Tasa',
        'quota': 'Couta',
        'exempt': 'Exento',
    }
    for old_value, new_value in values_to_fix.items():
        env.cr.execute("""
            UPDATE account_tax
            SET l10n_mx_tax_type = '%s'
            WHERE l10n_mx_tax_type = '%s'
        """ % (new_value, old_value))


def define_compay_fields(env):
    env.cr.execute("""
        UPDATE res_company
        SET
        account_cash_basis_base_account_id = 454,
        l10n_mx_edi_pac = 'finkok',
        l10n_mx_edi_pac_username = 'sitibt@odoo.com',
        l10n_mx_edi_pac_password = '16e4add63257a90965d62212782913488d4a2196d119fd92a637faa39db2',
        l10n_mx_edi_fiscal_regime = '601'
    """)


def process_tax_accounts(env):
    """ Tax accounts must have reconcile = True when tax cash basis is
    configured and you use multi currency
    """
    taxes = env['account.tax'].search([('tax_exigibility', '=', 'on_payment')])
    accounts = taxes.mapped('cash_basis_transition_account_id')
    accounts.write({
        'reconcile': True,
    })


def process_invoices(env):
    invoices = env['account.move'].search([
        ('move_type', '=', 'out_invoice'),
        ('state', '=', 'posted'),
    ])
    count = 1
    for invoice in invoices:
        _logger.warning('Processing invoice %s of %s' % (count, len(invoices)))
        count += 1
        attachment = env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', invoice.id),
            ('name', '=ilike', '%.xml'),
        ], limit=1)
        if not attachment:
            continue
        env['account.edi.document'].create({
            'move_id': invoice.id,
            'edi_format_id': env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
            'attachment_id': attachment.id,
            'state': 'sent',
        })
    payments = env['account.payment'].search([
        ('state', '=', 'posted'),
        ('payment_type', '=', 'inbound'),
    ])
    count = 1
    for payment in payments:
        _logger.warning('Processing payment %s of %s' % (count, len(payments)))
        count += 1
        attachment = env['ir.attachment'].search([
            ('res_model', '=', 'account.payment'),
            ('res_id', '=', payment.id),
            ('name', '=ilike', '%.xml'),
        ], limit=1)
        if not attachment:
            continue
        env['account.edi.document'].create({
            'move_id': payment.move_id.id,
            'edi_format_id': env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
            'attachment_id': attachment.id,
            'state': 'sent',
        })

def add_certificate(env):
    companies = env['res.company'].search([])
    for company in companies:
        env.cr.execute("""
            SELECT
                file_cer AS content,
                file_key AS key,
                password AS password,
                serial_number AS serial_number,
                date_start AS date_start,
                date_end AS date_end
            FROM res_certificate
            WHERE company_id = %(company_id)s
        """, {'company_id': company.id})
        certificates = env.cr.dictfetchall()
        for certificate in certificates:
            if certificate.get('date_end') < date.today():
                continue
            certificate = env['l10n_mx_edi.certificate'].create(certificate)
            company.write({
                'l10n_mx_edi_certificate_ids': [(4,certificate.id)],
            })


def add_currency_precision_for_mx(env):
    env.cr.execute("""
        UPDATE res_currency
        SET l10n_mx_edi_decimal_places = 2;
    """)


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Delete records from XML ID')
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    _logger.warning('Fix tax type.')
    fix_l10n_mx_cfdi_tax_type(env)
    _logger.warning('Define company fields.')
    define_compay_fields(env)
    _logger.warning('Add certificate to companies.')
    add_certificate(env)
    _logger.warning('Update tax cash basis tax account to reconciled')
    process_tax_accounts(env)
    _logger.warning('Reset base module to version 1.3')
    process_invoices(env)
    _logger.warning('Uninstalling not required modules')
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
    modules_to_remove.unlink()
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '15.0.1.3'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')