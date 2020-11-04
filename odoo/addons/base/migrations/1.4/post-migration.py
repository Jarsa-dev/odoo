# Copyright 2020, Mtnet Services, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openupgradelib import openupgrade
import logging
_logger = logging.getLogger(__name__)


modules_to_rename = [
    ('iho_security', 'iho'),
    ('ui_simplification', 'iho_simplification'),
]


@openupgrade.migrate()
def migrate(env, installed_version):
    env.cr.execute('delete from res_users_role_line where user_id is null;')
    openupgrade.update_module_names(env.cr, modules_to_rename, True)
