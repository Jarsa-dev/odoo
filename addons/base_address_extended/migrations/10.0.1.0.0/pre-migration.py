# coding: utf-8
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

column_renames = {
    'res_partner': [
        ('l10n_mx_street3', 'street_number'),
        ('l10n_mx_street4', 'street_number2'),
        ('street', 'street_name'),
    ]
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
