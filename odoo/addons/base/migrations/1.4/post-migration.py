# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

to_remove = [
    'l10n_mx_avoid_reversal_entry',
    'database_cleanup',
    'l10n_mx_edi_cancellation_complement',
]

to_install = []

models_to_rename = []

tables_to_rename = []

fields_to_rename = []


def rename_modules(env, old, new):
    env['ir.module.module'].update_list()
    _logger.warning(
        'Rename module %s -> %s' % (old, new))
    module = env['ir.module.module'].search(
        [('name', '=', new)])
    old_module = env['ir.module.module'].search(
        [('name', '=', old)])
    module.invalidate_cache()
    if module and old_module:
        env.cr.execute(
            "DELETE FROM ir_model_data WHERE name = 'module_%s'" % new)
        env.cr.execute(
            'DELETE FROM ir_module_module WHERE id = %s' % module.id)
        openupgrade.update_module_names(env.cr, [(old, new)])


@openupgrade.migrate()
def migrate(env, installed_version):
    # openupgrade.rename_models(env.cr, models_to_rename)
    # openupgrade.rename_tables(env.cr, tables_to_rename)
    # openupgrade.rename_fields(env, fields_to_rename)
    rename_modules(env, 'l10n_mx_edi_bank', 'l10n_mx')
    env['ir.module.module'].update_list()
    # modules_to_install = env['ir.module.module'].search([
    #     ('name', 'in', to_install)])
    # modules_to_install.button_install()
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
