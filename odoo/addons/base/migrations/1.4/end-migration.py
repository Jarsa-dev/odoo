# Copyright 2019 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def process_invoices(env):
    _logger.warning('Fix report name in account.invoice')
    env.cr.execute("UPDATE account_invoice SET l10n_mx_edi_cfdi_name = l10n_mx_edi_cfdi_name || '.xml'")
    invoices = env['account.invoice'].search([
        ('type', 'in', ['out_invoice', 'out_refund'])])
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
    _logger.warning('Compute CFDI Values to All Invoices')
    invoices._compute_cfdi_values()
    _logger.warning('Update SAT Status to All Invoices')
    invoices.l10n_mx_edi_update_sat_status()


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Define l10n_mx_edi_decimal_places to 2')
    env.cr.execute('UPDATE res_currency SET l10n_mx_edi_decimal_places = 2;')
    process_invoices(env)
