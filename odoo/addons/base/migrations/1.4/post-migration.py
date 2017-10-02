# coding: utf-8
# Copyright 2017 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env['ir.module.module'].update_list()
    env['ir.module.module'].search(
        [('name', '=',
            'account_tax_cash_basis_fix_currency_rate_difference_analytic')
         ]).unlink()
    openupgrade.update_module_names(
        env.cr,
        [('account_tax_cash_basis_fix_currency_rate_difference',
          'account_tax_cash_basis_fix_currency_rate_difference_analytic')])
    openupgrade.logged_query(
        env.cr, '''
        UPDATE ir_module_module
        SET latest_version='1.3'
        WHERE name='base';
        ''')
