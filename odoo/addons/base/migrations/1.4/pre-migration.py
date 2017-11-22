# coding: utf-8
# Copyright 2017 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

def delete_views(cr):
    cr.execute("DELETE FROM ir_ui_view WHERE name='res.users.form.inherit';")
    cr.execute("DELETE FROM ir_ui_view WHERE name='res.users.form.mail';")
    cr.execute("DELETE FROM ir_ui_view WHERE name='res.users.groups';")
    cr.execute("DELETE FROM ir_ui_view WHERE name='res.users.form';")


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env.cr.execute("DELETE FROM ir_model_data WHERE name='module_web_gantt';")
    delete_views(env.cr)

