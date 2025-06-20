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
    "partner_group",
    "mail_restrict_follower_selection",
    "account_tax_cash_basis_reference",
    "product_expiry",
]


# List of strings with XML ID.
records_to_remove = [
]


views_to_activate = [
    "purchase_operating_unit.purchase_order_form",
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
    if views_to_activate:
        _logger.warning('Activating views')
        for view in views_to_activate:
            view_record = env.ref(view, raise_if_not_found=False)
            if view_record:
                view_record.active = True
            else:
                _logger.warning(f'View {view} not found')
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '17.0.1.4'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
    _logger.warning('The migration has finished')
