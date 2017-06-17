# coding: utf-8
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

SQL = (
    "UPDATE ir_module_module SET latest_version='9.0.2.1.0', "
    "state='to upgrade' WHERE name IN ('base_address_extended', "
    "'base_address_city', 'analytic_operating_unit');")


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env['ir.module.module'].update_list()
    env['ir.module.module'].search([('name', '=', 'l10n_mx_base')]).unlink()
    # MT Views
    env.ref('comandos_invoice.report_xml_invoice_page').unlink()
    env.ref('comandos_invoice.report_xml_invoice_header').unlink()
    # OML Views
    env.ref('oml.electronic_invoice_report_document').unlink()
    env.ref('oml.external_layout').unlink()
    env.ref('oml.external_layout_footer').unlink()
    env.ref('oml.external_layout_header').unlink()
    env.ref('oml.ir_sequence_form_oml').unlink()
    env.ref('oml.l10n_mx_edi_addenda_autozone').unlink()
    env.ref('oml.l10n_mx_edi_addenda_bosh_A_C').unlink()
    env.ref('oml.res_partner_account_form_oml').unlink()
    env.ref('oml.res_partner_address_form_oml').unlink()
    env.ref('oml.res_partner_form_oml').unlink()
    env.ref('oml.view_account_account_inherit_form').unlink()
    env.ref('oml.view_account_addenda_form').unlink()
    env.ref('oml.view_account_addenda_tree').unlink()
    env.ref('oml.view_account_invoice_attachment_mx_supplier').unlink()
    env.ref('oml.view_account_invoice_form_oml').unlink()
    env.ref('oml.view_account_invoice_search_inh_oml').unlink()
    env.ref('oml.view_account_invoice_supplier_form_inh_oml').unlink()
    env.ref('oml.view_account_journal_view_form_inh_oml').unlink()
    env.ref('oml.view_account_tax_category_form').unlink()
    env.ref('oml.view_account_tax_category_form_inh').unlink()
    env.ref('oml.view_account_tax_category_search').unlink()
    env.ref('oml.view_account_tax_category_tree').unlink()
    env.ref('oml.view_addenda_fields_form').unlink()
    env.ref('oml.view_addenda_fields_tree').unlink()
    env.ref('oml.view_country_state_city_form').unlink()
    env.ref('oml.view_country_state_city_tree').unlink()
    env.ref('oml.view_oml_account_tag_tree').unlink()
    env.ref('oml.view_oml_acount_tag_form').unlink()
    env.ref('oml.view_oml_payment_method_form').unlink()
    env.ref('oml.view_oml_payment_method_tree').unlink()
    env.ref('oml.view_partner_bank_clabe_form_inh_xml').unlink()
    env.ref('oml.view_partner_bank_clabe_tree_inh_xml').unlink()
    env.ref('oml.view_regimen_fiscal_form').unlink()
    env.ref('oml.view_regimen_fiscal_tree').unlink()
    env.ref('oml.view_res_bank_inherit_oml').unlink()
    env.ref('oml.view_res_certificate_form').unlink()
    env.ref('oml.view_res_certificate_search').unlink()
    env.ref('oml.view_res_certificate_tree').unlink()
    env.ref('oml.view_res_company_form_oml').unlink()
    env.ref('oml.view_res_pac_form').unlink()
    env.ref('oml.view_res_pac_search').unlink()
    env.ref('oml.view_res_pac_tree').unlink()
    env.ref('oml.view_wizard_update_fiscal_information_sat').unlink()
    env.ref('oml.view_wizard_validate_invoice_uuid_sat').unlink()
    env.ref('oml.view_wizard_xml_to_validate_line_sat').unlink()
    env.cr.execute(SQL)
    openupgrade.update_module_names(env.cr, [('oml', 'l10n_mx_base')])
    env.cr.execute('''
        UPDATE ir_module_module
        SET latest_version='1.3'
        WHERE name='base';
        ''')
