# coding: utf-8
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

SQL = '''
    UPDATE ir_module_module
    SET latest_version='10.0.1.0.0', state='to upgrade'
    WHERE name IN (
    'l10n_mx_edi_bank',
    'l10n_mx_edi_attachment',
    'l10n_mx_edi_partner_defaults');
    '''


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env['ir.module.module'].update_list()
    env['ir.module.module'].search([('name', '=', 'l10n_mx_edi')]).unlink()
    openupgrade.update_module_names(env.cr, [('l10n_mx_base', 'l10n_mx_edi')])
    env.cr.execute(SQL)
    env.cr.execute('''
        UPDATE ir_module_module
        SET latest_version='1.3'
        WHERE name='base';
        ''')
