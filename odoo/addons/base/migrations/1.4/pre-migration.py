# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Removing bank accounts with no partner')
    env.cr.execute('DELETE FROM res_partner_bank WHERE partner_id IS NULL;')
    _logger.warning('Replacing state to partners')
    env.cr.execute(
        'UPDATE res_partner SET state_id = 535 WHERE state_id = 74;')
    _logger.warning('Remove repeated state')
    env.cr.execute('DELETE FROM res_country_state WHERE id = 74;')
    _logger.warning('Remove currencies with no symbol')
    env.cr.execute('DELETE FROM res_currency WHERE symbol IS NULL;')
    _logger.warning(
        'Remove duplicated account_financial_html_report_line PASCIRPRV and '
        'PASCIRDPP')
    env.cr.execute("""
        DELETE FROM account_financial_html_report_line
        WHERE id IN (449, 451);
    """)
    _logger.warning(
        'Rename duplicated account_financial_html_report_line PAS -> PVO')
    env.cr.execute("""
        UPDATE account_financial_html_report_line
        SET code = 'PVO'
        WHERE id = 454;
    """)
    _logger.warning(
        'Update formula account_financial_html_report_line to adapt code '
        'change PAS -> PVO')
    env.cr.execute("""
        UPDATE account_financial_html_report_line
        SET formulas = 'balance=PVO.balance+CAP.balance'
        WHERE id = 444;
    """)
    _logger.warning('Assign correct currency to Guinea-Bissauan')
    env.cr.execute('UPDATE res_country SET currency_id = 42 WHERE id = 93;')
    _logger.warning('Remove duplicated SAT code 72101511')
    env.cr.execute(
        'DELETE FROM l10n_mx_edi_product_sat_code WHERE id = 54572;')
    _logger.warning('Remove SAT Codes external id and regenerate the updated')
    env.cr.execute(
        "DELETE FROM ir_model_data WHERE name LIKE 'l10n_mx_edi_sat_code_%';")
    env.cr.execute("""
        INSERT INTO ir_model_data
        (name, res_id, module, model)
        SELECT concat('prod_code_sat_', code), id, 'l10n_mx_edi',
        'l10n_mx_edi.product.sat.code'
        FROM l10n_mx_edi_product_sat_code;
    """)
