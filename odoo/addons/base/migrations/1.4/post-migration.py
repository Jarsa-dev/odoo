# Copyright 2020, Mtnet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openupgradelib import openupgrade
import logging
_logger = logging.getLogger(__name__)


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
    env.cr.execute('delete from res_users_role_line where user_id is null;')
    # env.cr.execute('alter table res_lang drop constraint res_lang_code_uniq cascade;')
    rename_modules(env, 'iho_security', 'iho')
    rename_modules(env, 'ui_simplification', 'iho_simplification')
