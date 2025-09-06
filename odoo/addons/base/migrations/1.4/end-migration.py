# Copyright 2022 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from openupgradelib import openupgrade
from odoo.tools import float_compare

import datetime

_logger = logging.getLogger(__name__)


to_remove = [
    "l10n_mx_edi_partner_defaults",
    "l10n_mx_edi_statement_cancellation",
    "l10n_mx_edi_uuid",
    "l10n_mx_edi_uuid_zip",
    "sale_subscription_operating_unit",
    "account_cash_basis_mix_currency_fix",
    "partner_group",
    "mail_restrict_follower_selection",
    "account_tax_cash_basis_reference",
    "product_expiry",
]


# List of strings with XML ID.
records_to_remove = [
]


views_to_activate = [
    "purchase_operating_unit.purchase_order_form",
    "mtnmx.mtnet_account_move_form",
    "l10n_mx_edi_refund.view_account_move_reversal_mx_edi",
    "mtnmx.account_move_line_tree_customization",
    "account_move_tier_validation.view_account_invoice_filter",
    "account_analytic_tag_assign.account_invoice_supplier_tree_customization",
    "tier_validation_mtnmx.account_invoice_supplier_tree_customization",
    "account_move_name_sequence.view_move_form",
    "operating_unit_mtnmx.account_move_operating_unit_form_mtnmx",
    "account_analytic_tag_assign.account_invoice_mtnmx",
    "account_analytic_tag_assign.account_move_line_maint_mtnmx_tree",
    "queue_job.view_queue_job_form",
    "product_brand.view_product_template_kanban_brand",
    "product_brand.view_product_variant_kanban_brand",
    "account_analytic_tag_assign.product_brand_mtnmx",
    "sql_export.sql_export_view_form",
    "costing_worksheet_mtnmx.view_costing_worksheet_search",
    "mail_activity_board.mail_activity_view_kanban",
    "mail_activity_team.mail_activity_view_kanban",
    "project_template.project_template_view_inherit_form",
    "project_timeline.project_project_form",
    "sales_team_operating_unit.crm_team_view_form",
    "mail_tracking_mailgun.res_config_settings_view_form",
    "account_usability.res_config_settings_view_form",
    "sat_download_metadata.res_config_settings_view_form_sat_metadata",
    "hr_leave_expiration.leave_expiration_res_config_settings_view_form",
    "account_budget_mtnmx.res_config_settings_view_form_default_budget_analytic",
    "costing_worksheet_mtnmx.res_config_settings_view_form_purchase_costing_worksheet",
    "mtnmx.ir_action_server_mtnmx",
    "operating_unit.view_users_form",
    "base_location.view_company_form_city",
    "account_analytic_tag_assign.purchase_order_mtnmx",
    "account_budget_mtnmx.purchase_order_budget_mtnmx",
    "purchase_tier_validation.view_purchase_order_filter",
    "l10n_mx.res_config_settings_view_form",
    "operating_unit_mtnmx.purchase_order_operating_unit_form_mtnmx",
    "project_parent_task_filter.view_task_search_form",
    "project_timeline.project_task_timeline",
    "project_timeline.view_task_form2",
    "project_timeline.view_task_tree2",
    "engineer_certifications_mtnmx.project_task_engineer_certifications_form",
    "operating_unit_mtnmx.analytic_analytic_account_form_mtnmx",
    "account_budget_mtnmx.budget_analytic_mtnmx_form",
    "costing_worksheet_mtnmx.analytic_account_costing_worksheet_form_mtnmx",
    "purchase_order_pivot.purchase_order_line_tree_search",
    "purchase_order_pivot.purchase_order_line_tree_view",
    "purchase_order_pivot.purchase_order_lines_pivot_rwnippm_view",
    "purchase_order_pivot.purchase_order_lines_pivot_rwnippw_view",
    "purchase_order_pivot.purchase_order_lines_pivot_trppm_view",
    "purchase_order_pivot.purchase_order_lines_pivot_trppw_view",
]


def _process_edi_files(env):
    _logger.warning('Processing EDI files')
    edi_documents = env['l10n_mx_edi.document'].search([])
    attachments = env["ir.attachment"].search([
        ("res_model", "=", "account.move"),
        ("name", "=ilike", "%.xml"),
        ("res_id", "not in", edi_documents.mapped('move_id').ids),
        ("res_id", "!=", False),
    ])
    _logger.warning(f'Found {len(attachments)} attachments to process')
    count = 0
    for attachment in attachments:
        count += 1
        attachment_id = attachment.id
        res_id = attachment.res_id
        if count % 100 == 0:
            _logger.warning(f'Processing attachment {count}/{len(attachments)}')
        try:
            with env.cr.savepoint():
                env['l10n_mx_edi.document'].create({
                    'move_id': attachment.res_id,
                    'invoice_ids': [(4, attachment.res_id)],
                    'state': 'invoice_sent',
                    'sat_state': 'not_defined',
                    'attachment_id': attachment.id,
                    'datetime': datetime.datetime.now(),
                })
        except Exception as e:
            _logger.warning(f'Error processing attachment {attachment_id} for move {res_id}: {e}')


def _archive_jornals(env):
    to_archive = [112, 134, 179, 214, 224, 251]
    env['account.journal'].browse(to_archive).write({'active': False})


def _process_diot_fix(env):
    _logger.warning('Processing DIOT fix')
    map_tax_tags = {
        "+DIOT: 16% NO ACREDITABLE": "+DIOT: 16% NO ACREDITABLE TAX",
    }
    for old_tag, new_tag in map_tax_tags.items():
        old_tag_rec = env['account.account.tag'].search([('name', '=', old_tag)], limit=1)
        new_tag_rec = env['account.account.tag'].search([('name', '=', new_tag)], limit=1)
        env.cr.execute("""
            UPDATE account_account_tag_account_move_line_rel
            SET account_account_tag_id = %(new_id)s
            WHERE account_account_tag_id = %(old_id)s;
        """, {
            'new_id': new_tag_rec.id,
            'old_id': old_tag_rec.id,
        })
        env.cr.execute("""
            UPDATE account_account_tag_account_tax_repartition_line_rel
            SET account_account_tag_id = %(new_id)s
            WHERE account_account_tag_id = %(old_id)s;
        """, {
            'new_id': new_tag_rec.id,
            'old_id': old_tag_rec.id,
        })

@openupgrade.migrate()
def migrate(env, installed_version):
    if records_to_remove:
        _logger.warning('Delete records from XML ID')
        openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    if to_remove:
        _logger.warning('Uninstalling not required modules')
        modules_to_remove = env['ir.module.module'].search([
            ('name', 'in', to_remove)])
        modules_to_remove += modules_to_remove.downstream_dependencies()
        modules_to_remove.module_uninstall()
        modules_to_remove.unlink()
    if views_to_activate:
        _logger.warning('Activating views')
        for view in views_to_activate:
            view_record = env.ref(view, raise_if_not_found=False)
            if view_record:
                try:
                    view_record.active = True
                except Exception as e:
                    _logger.warning(f'Error activating view {view}: {e}')
            else:
                _logger.warning(f'View {view} not found')
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '17.0.1.4'
        WHERE name = 'base';
    """)
    env.ref("account_reports.menu_action_account_report_gt").write({
        "groups_id": [(5,0,0)],
    })
    env.cr.execute("DELETE FROM base_automation WHERE id = 8;")
    env.cr.execute("DELETE FROM ir_config_parameter WHERE key = 'report.url';")
    _process_edi_files(env)
    _archive_jornals(env)
    # _process_diot_fix(env)
    _logger.warning('The migration has finished')
    