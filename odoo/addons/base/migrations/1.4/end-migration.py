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
    count = 0
    total_count = 0
    for invoice in invoices:
        invoice.l10n_mx_edi_update_sat_status()
        count += 1
        if count == 100:
            total_count += count
            count = 0
            _logger.warning('Invoices processed %s of %s' % (
                total_count, len(invoices)))
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


def fix_fiscal_positions(env):
    fpos = env['account.fiscal.position'].search([])
    for position in fpos:
        name_split = position.name.split('-')
        if len(name_split) > 1:
            position.l10n_mx_edi_code = name_split[0].strip()


def fix_l10n_mx_cfdi_tax_type(env):
    values_to_fix = {
        'rate': 'Tasa',
        'quota': 'Couta',
        'exempt': 'Exento',
    }
    for old_value, new_value in values_to_fix.items():
        env.cr.execute("""
            UPDATE account_tax
            SET l10n_mx_cfdi_tax_type = '%s'
            WHERE l10n_mx_cfdi_tax_type = '%s'
        """ % (new_value, old_value))


def process_tax_tags_groups(env):
    # New tax tags
    tag_iva_id = env.ref('l10n_mx.tag_iva').id
    tag_isr_id = env.ref('l10n_mx.tag_isr').id
    tag_ieps_id = env.ref('l10n_mx.tag_ieps').id
    tag_diot_16_id = env.ref('l10n_mx.tag_diot_16').id
    tag_diot_16_non_cre_id = env.ref('l10n_mx.tag_diot_16_non_cre').id
    tag_diot_16_imp_id = env.ref('l10n_mx.tag_diot_16_imp').id
    tag_diot_0_id = env.ref('l10n_mx.tag_diot_0').id
    tag_diot_8_id = env.ref('l10n_mx.tag_diot_8').id
    tag_diot_8_non_cre_id = env.ref('l10n_mx.tag_diot_8_non_cre').id
    tag_diot_ret_id = env.ref('l10n_mx.tag_diot_ret').id
    tag_diot_exento_id = env.ref('l10n_mx.tag_diot_exento').id

    # New tax groups
    group_taxes_id = env.ref('account.tax_group_taxes').id
    group_iva_0_id = env.ref('l10n_mx.tax_group_iva_0').id
    group_iva_16_id = env.ref('l10n_mx.tax_group_iva_16').id
    group_iva_8_id = env.ref('l10n_mx.tax_group_iva_8').id
    group_iva_ret_4_id = env.ref('l10n_mx.tax_group_iva_ret_4').id
    group_iva_ret_10_id = env.ref('l10n_mx.tax_group_iva_ret_10').id
    group_iva_ret_1067_id = env.ref('l10n_mx.tax_group_iva_ret_1067').id
    group_isr_ret_10_id = env.ref('l10n_mx.tax_group_isr_ret_10').id

    taxes_dict = {
        # 16% Ventas
        '42,70,124,144': {
            'tax_group_id': group_iva_16_id,
            'tag_ids': [(6, 0, [tag_iva_id])],
        },
        # 16% Compras No Deducibles
        '53,197,137': {
            'tax_group_id': group_iva_16_id,
            'tag_ids': [(6, 0, [tag_diot_16_non_cre_id])],
        },
        # IEPS 8% Compras
        '160,198': {
            'tag_ids': [(6, 0, [tag_ieps_id])],
        },
        # IVA Ventas 8%
        '163,179,182': {
            'tax_group_id': group_iva_8_id,
            'tag_ids': [(6, 0, [tag_iva_id])],
        },
        # IVA Compras 8%
        '164,174,183': {
            'tax_group_id': group_iva_8_id,
            'tag_ids': [(6, 0, [tag_diot_8_id])],
        },
        # IVA Compras 8% No Deducibles
        '165,175': {
            'tax_group_id': group_iva_8_id,
            'tag_ids': [(6, 0, [tag_diot_8_non_cre_id])],
        },
        # RETENCION IVA 5.33% Compras
        '167': {
            'tax_group_id': group_taxes_id,
            'tag_ids': [(6, 0, [tag_diot_ret_id])],
        },
        # RET IVA 6% Compras
        '187,189': {
            'tax_group_id': group_taxes_id,
            'tag_ids': [(6, 0, [tag_diot_ret_id])],
        },
        # RET ISR PAGOS EXTRANJERO 10% Compras
        '191,184': {
            'tax_group_id': group_iva_ret_10_id,
            'tag_ids': [(6, 0, [tag_isr_id])],
        },
        # RET IVA 3% Compras
        '194': {
            'tax_group_id': group_taxes_id,
            'tag_ids': [(6, 0, [tag_diot_ret_id])],
        },
        # RET IVA 6% Ventas
        '200,186': {
            'tax_group_id': group_taxes_id,
            'tag_ids': [(6, 0, [tag_iva_id])],
        },
        # RET IVA 3% Ventas
        '201,199': {
            'tax_group_id': group_taxes_id,
            'tag_ids': [(6, 0, [tag_iva_id])],
        },
        # IVA 16% Compras
        '43,90,126,153': {
            'tax_group_id': group_iva_16_id,
            'tag_ids': [(6, 0, [tag_diot_16_id])],
        },
        # IVA Exento Compras
        '49,91,127,154': {
            'tax_group_id': group_iva_0_id,
            'tag_ids': [(6, 0, [tag_diot_exento_id])],
        },
        # IVA 0% Compras
        '51,92,128,151': {
            'tax_group_id': group_iva_0_id,
            'tag_ids': [(6, 0, [tag_diot_0_id])],
        },
        # RET ISR Honorarios 10% Compra
        '44,93,129,148': {
            'tax_group_id': group_isr_ret_10_id,
            'tag_ids': [(6, 0, [tag_isr_id])],
        },
        # RET IVA FLETES 4% Compra
        '47,94,130,145': {
            'tax_group_id': group_iva_ret_4_id,
            'tag_ids': [(6, 0, [tag_diot_ret_id])],
        },
        # RET ISR ARRENDAMIENTO 10% Compra
        '41,95,131,147': {
            'tax_group_id': group_isr_ret_10_id,
            'tag_ids': [(6, 0, [tag_isr_id])],
        },
        # RETENCION IVA HONORARIOS 10.67% Compra
        '46,96,132,150': {
            'tax_group_id': group_iva_ret_1067_id,
            'tag_ids': [(6, 0, [tag_diot_ret_id])],
        },
        # RETENCION IVA ARRENDAMIENTO 10.67% Compra
        '45,97,133,149': {
            'tax_group_id': group_iva_ret_1067_id,
            'tag_ids': [(6, 0, [tag_diot_ret_id])],
        },
    }
    for ids, data in taxes_dict.items():
        id_list = ids.split(',')
        for id in id_list:
            env['account.tax'].browse(int(id)).write(data)

    _logger.warning('Remove old tax tags.')
    env['account.account.tag'].browse(
        [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]).unlink()
    _logger.warning('Remove old tax groups.')
    env['account.tax.group'].browse(
        [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13]).unlink()


def regenerate_reports_menu(env):
    reports = env['account.financial.html.report'].browse([1, 2])
    for report in reports:
        parent_id = report.parent_id.id
        report.generated_menu_id.action.unlink()
        report.generated_menu_id.unlink()
        report._create_action_and_menu(parent_id)


def define_tax_cash_basis_account(env):
    for data in [('4076', '1'), ('4077', '3'), ('4078', '4'), ('4079', '6')]:
        env.cr.execute("""
            UPDATE account_tax
            SET cash_basis_base_account_id = %s
            WHERE tax_exigibility = 'on_payment'
            AND company_id = %s
        """, data)


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Define tax cash basis account in taxes.')
    define_tax_cash_basis_account(env)
    _logger.warning('Regenerate Account Reports Menus.')
    regenerate_reports_menu(env)
    _logger.warning('Change tax tags and tax groups to taxes.')
    process_tax_tags_groups(env)
    _logger.warning('Fix code of fiscal positions.')
    fix_fiscal_positions(env)
    _logger.warning('Fix tax type.')
    fix_l10n_mx_cfdi_tax_type(env)
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
