# coding: utf-8
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

SQL = (
    "UPDATE ir_module_module SET latest_version='10.0.0.0.0', "
    "state='to upgrade' WHERE name IN ('base_address_extended', "
    "'base_address_city', 'l10n_mx_base');")

SQL2 = (
    "UPDATE ir_module_module SET state='to upgrade'"
    "WHERE name IN ('web_enterprise', 'currency_rate_live', 'account_reports');")

def change_vat(cr):
    cr.execute('''
        UPDATE res_partner
        SET vat=substring(vat, 3)
        WHERE vat ILIKE 'MX%';''')
    cr.execute('''
        UPDATE res_partner
        SET vat=replace(vat, ' ', '')
        WHERE vat ILIKE '% %';''')

column_renames = {  
    'account_journal': [
        ('address_invoice_company_id', 'address_issued_id'),
    ],
    'account_invoice': [
        ('sello', 'sello2'),
        ('cfdi_sello', 'sello'),
        ('cfdi_no_certificado', 'certificate_number'),
        ('cfdi_cadena_original', 'cfdi_original_string'),
        ('cfdi_fecha_timbrado', 'date_stamped'),
        ('cfdi_fecha_cancelacion', 'cfdi_cancellation_date'),
        ('cfdi_folio_fiscal', 'cfdi_uuid'),
        ('invoice_sequence_id', 'sequence_id'),
        ('pay_method_id', 'l10n_mx_payment_method_id'),
        ('acc_payment', 'account_payment_id'),
    ],
}

table_renames = [
    ('pay_method', 'l10n_mx_payment_method'),
]

model_renames = [
    ('pay.method', 'l10n_mx.payment.method'),
]

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # env['ir.module.module'].update_list()
    # env['ir.module.module'].search([('name', '=', 'l10n_mx_base')]).unlink()
    env.cr.execute(SQL)
    env.cr.execute(SQL2)
    env.cr.execute("ALTER TABLE pay_method DROP CONSTRAINT pay_method_code_uniq;")
    env.cr.execute("ALTER TABLE pay_method DROP CONSTRAINT pay_method_name_uniq;")
    change_vat(env.cr)
    openupgrade.rename_models(env.cr, model_renames)
    openupgrade.rename_tables(env.cr, table_renames)
    openupgrade.rename_columns(env.cr, column_renames)
    # env.cr.execute('''
    #     UPDATE ir_module_module
    #     SET latest_version='1.3'
    #     WHERE name='base';
    #     ''')

