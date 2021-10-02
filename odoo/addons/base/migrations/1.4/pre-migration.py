# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Start Migration')
    _logger.warning('Delete auditlog rule')
    env.cr.execute("DELETE FROM auditlog_rule WHERE model_id IS NULL;")
    _logger.warning('Delete role line rule')
    env.cr.execute("DELETE FROM res_users_role_line WHERE user_id  IS NULL;")
    # _logger.warning('Delete quality_check line rule')
    # env.cr.execute("DELETE FROM quality_check WHERE test_type_id IS NULL;")
    _logger.warning('Delete mail_template not loaded')
    env.cr.execute("DELETE FROM mail_template WHERE id = 21;")
    env.cr.execute("""
        DELETE FROM ir_model_data
        WHERE
        module = 'mrp_production_limit' AND
        name = 'send_mail_alert_production';
    """)
