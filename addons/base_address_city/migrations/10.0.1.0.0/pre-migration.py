# coding: utf-8
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

table_renames = [
    ('res_country_state_city', 'res_city'),
]

model_renames = [
    ('res.country.state.city', 'res.city'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_models(env.cr, model_renames)
    openupgrade.rename_tables(env.cr, table_renames)
