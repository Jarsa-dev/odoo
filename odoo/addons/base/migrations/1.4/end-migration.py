# Copyright 2022 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from openupgradelib import openupgrade
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


to_remove = [
    "l10n_mx_edi_partner_defaults",
    "l10n_mx_edi_statement_cancellation",
    "l10n_mx_edi_uuid",
    "l10n_mx_edi_uuid_zip",
    "sale_subscription_operating_unit",
    "account_cash_basis_mix_currency_fix",
    "mis_builder",
    "partner_group",
    "mail_restrict_follower_selection",
    "account_tax_cash_basis_reference",
    "product_expiry",
]


# List of strings with XML ID.
records_to_remove = [
]


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
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '17.0.1.4'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
    _logger.warning('The migration has finished')
