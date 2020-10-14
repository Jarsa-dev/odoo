# Copyright 2020, Mtnet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, installed_version):
    env.cr.execute('delete from res_users_role_line where user_id is null;')
    # env.cr.execute('alter table res_lang drop constraint res_lang_code_uniq cascade;')
    openupgrade.update_module_names(env.cr, [('iho_security','iho')], True)
