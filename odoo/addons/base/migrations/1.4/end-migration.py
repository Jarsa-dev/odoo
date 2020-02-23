# Copyright 2019 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from openupgradelib import openupgrade
from lxml.etree import XMLSyntaxError

_logger = logging.getLogger(__name__)


records_to_remove = [
    'l10n_mx_edi.action_rule_write_create_ping_pac_server',
    'l10n_mx_edi.action_rule_write_create_check_color_tag_server',
    'l10n_mx_edi.action_rule_write_create_update_hour',
    'l10n_mx_edi.ir_cron_update_sat_status',
    'l10n_mx_edi.ir_cron_cancel_invoices_xml',
    'l10n_mx_edi.ir_cron_update_fiscal_information',
    'l10n_mx_edi.action_res_pac',
    'l10n_mx_edi.menu_res_pac',
    'l10n_mx_edi.menu_pacs',
    'l10n_mx_edi.action_res_certificate_tree',
    'l10n_mx_edi.menu_res_certificate',
    'l10n_mx_edi.group_l10n_mx_base_user',
    'l10n_mx_edi.group_l10n_mx_base_manager',
    'l10n_mx_edi_cancellation.ir_cron_cancellation_invoices_cancel_signed_sat',
    'l10n_mx_edi.ping_pac_server_action',
    'l10n_mx_edi_cancellation.ir_cron_cancellation_invoices_cancel_signed_sat_ir_actions_server',
    'l10n_mx_edi.l10n_mx_facturae_mx_cer_rule',
    'l10n_mx_edi.sat_digital_certificate',
]


def process_invoices(env):
    _logger.warning('Fix report name in account.invoice')
    env.cr.execute("""
        UPDATE account_invoice
        SET l10n_mx_edi_cfdi_name = l10n_mx_edi_cfdi_name || '.xml'
        WHERE l10n_mx_edi_cfdi_name IS NOT NULL;
    """)
    mex_or_false = [env.ref('base.mx').id, False]
    invoices = env['account.invoice'].search([
        ('company_id.partner_id.country_id', '=', env.ref('base.mx').id),
        '|', ('partner_id.country_id', 'in', mex_or_false),
        ('partner_id.commercial_partner_id.country_id', 'in', mex_or_false)
    ])
    cancelled_invoices = invoices.filtered(lambda i: i.state == 'cancel')
    _logger.warning('Define PAC Status to Cancelled Invoices')
    cancelled_invoices.write({
        'l10n_mx_edi_pac_status': 'cancelled'
    })
    open_invoices = invoices.filtered(
        lambda i: i.state not in ['cancel', 'draft'])
    _logger.warning('Define PAC Status to Signed Invoices')
    open_invoices.write({
        'l10n_mx_edi_pac_status': 'signed'
    })
    _logger.warning('Compute CFDI Values to All Invoices (%s)' % len(invoices))
    failed = []
    count = 0
    total_count = 0
    for invoice in invoices:
        try:
            invoice._compute_cfdi_values()
        except XMLSyntaxError:
            failed.append(str(invoice.id))
            invoices -= invoice
        count += 1
        if count == 100:
            total_count += count
            count = 0
            _logger.warning('Invoices processed %s of %s' % (
                total_count, len(invoices)))
    _logger.warning('Update SAT Status to All Invoices')
    invoices.l10n_mx_edi_update_sat_status()
    _logger.warning('Failed Invoices: %s' % ','.join(failed))


def process_tax_accounts(env):
    """ Tax accounts must have reconcile = True when tax cash basis is
    configured and you use multi currency
    """
    accounts = env['account.account']
    taxes = env['account.tax'].search([('tax_exigibility', '=', 'on_payment')])
    accounts |= taxes.mapped('account_id')
    accounts |= taxes.mapped('refund_account_id')
    accounts.write({
        'reconcile': True,
    })


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Move report menu to correct account menu.')
    env.ref('account.menu_finance_reports').parent_id = env.ref(
        'account_accountant.menu_accounting').id
    _logger.warning('Update tax cash basis tax account to reconciled')
    process_tax_accounts(env)
    _logger.warning('Define l10n_mx_edi_decimal_places to 2')
    env.cr.execute('UPDATE res_currency SET l10n_mx_edi_decimal_places = 2;')
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    process_invoices(env)
    _logger.warning('Reset base module to version 1.3')
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '12.0.1.3'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
