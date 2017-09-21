# coding: utf-8
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

SQL = (
    "UPDATE ir_model_data SET module='__initial_data__' "
    "WHERE module='initial_data';")


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env['ir.module.module'].update_list()
    env.cr.execute(SQL)
    env['ir.module.module'].search([
        ('name', '=', 'initial_data')]).module_uninstall()
    env['ir.module.module'].search([
        ('name', 'in', ['l10n_mx', 'initial_data'])]).unlink()
    openupgrade.update_module_names(env.cr, [('l10n_mx_siti', 'l10n_mx')])
    env.cr.execute('''
        UPDATE ir_module_module
        SET latest_version='1.3'
        WHERE name='base';
        ''')
