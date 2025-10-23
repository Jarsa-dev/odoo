# Copyright 2022 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from openupgradelib import openupgrade
from odoo.tools import float_compare

from dateutil.relativedelta import relativedelta

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
    "account_tax_cash_basis_reference",
    "product_expiry",
    "purchase_analytic",
]


templates_to_reset = [
    "calendar.calendar_template_meeting_update",
    "calendar.calendar_template_meeting_changedate",
    "calendar.calendar_template_meeting_invitation",
    "calendar.calendar_template_meeting_reminder",
    "website_slides.mail_template_channel_shared",
    "base_install_request.mail_template_base_install_request",
    "hr_presence.mail_template_presence",
    "website_slides_survey.mail_template_user_input_certification_failed",
    "survey.mail_template_user_input_invite",
    "survey.mail_template_certification",
    "documents_hr.mail_template_document_folder_link",
    "stock.mail_template_data_delivery_confirmation",
    "account.email_template_edi_invoice",
    "mail_group.mail_template_guidelines",
    "mail_group.mail_template_list_subscribe",
    "mail_group.mail_template_list_unsubscribe",
    "timesheet_grid.mail_template_timesheet_reminder_user",
    "timesheet_grid.mail_template_timesheet_reminder",
    "timesheet_grid.mail_template_timesheet_reminder_manager",
    "gamification.email_template_badge_received",
    "gamification.simple_report_template",
    "gamification.email_template_goal_reminder",
    "account.email_template_edi_credit_note",
    "iap_extract.iap_extract_no_credit",
    "crm_iap_mine.lead_generation_no_credits",
    "purchase.email_template_edi_purchase_done",
    "purchase.email_template_edi_purchase",
    "purchase.email_template_edi_purchase_reminder",
    "sale.mail_template_sale_confirmation",
    "sale.email_template_edi_sale",
    "website_profile.validation_email",
    "portal.mail_template_data_portal_welcome",
    "hr_recruitment_survey.mail_template_applicant_interview_invite",
    "account.mail_template_data_payment_receipt",
    "hr_recruitment.email_template_data_applicant_congratulations",
    "hr_recruitment.email_template_data_applicant_interest",
    "hr_recruitment.email_template_data_applicant_refuse",
    "hr_recruitment.email_template_data_applicant_not_interested",
    "account_followup.email_template_followup_1",
    "account_online_synchronization.email_template_sync_reminder",
    "auth_signup.set_password_email",
    "auth_signup.mail_template_user_signup_account_created",
    "auth_signup.mail_template_data_unregistered_users",
    "website_payment.mail_template_donation",
    "documents.mail_template_document_request",
    "documents.mail_template_document_request_reminder",
    "sale_subscription.mail_template_subscription_alert",
    "sale_subscription.email_payment_close",
    "sale_subscription.mail_template_subscription_invoice",
    "sale_subscription.email_payment_success",
    "sale_subscription.email_payment_reminder",
    "sale_subscription.mail_template_subscription_rating",
    "project.mail_template_data_project_task",
    "helpdesk.new_ticket_request_email_template",
    "helpdesk.solved_ticket_request_email_template",
    "helpdesk.rating_ticket_request_email_template",
    "gamification.mail_template_data_new_rank_reached",
    "hr_appraisal.mail_template_appraisal_confirm",
    "hr_appraisal_survey.mail_template_appraisal_ask_feedback",
    "hr_appraisal.mail_template_appraisal_request_from_employee",
    "hr_appraisal.mail_template_appraisal_request",
    "sale.mail_template_sale_cancellation",
    "sale.mail_template_sale_payment_executed",
    "website_slides.mail_template_slide_channel_enroll",
    "website_slides.slide_template_shared",
    "website_slides.mail_template_slide_channel_invite",
    "website_slides.slide_template_published",
    "website_slides.mail_template_channel_completed",
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

jornals_to_archive = [
    112, 134, 140, 143, 179, 211, 214, 224, 251, 252, 425
]


def _archive_jornals(env):
    _logger.warning('Archiving journals')
    env['account.journal'].browse(jornals_to_archive).write({'active': False})

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


def _process_diot_fix(env):
    _logger.warning('Processing DIOT fix')
    map_tax_tags = {
        "+DIOT: 16% NO ACREDITABLE": "+DIOT: 16% NO ACREDITABLE TAX",
        "+DIOT: 8% N. NO ACREDITABLE": "+DIOT: 8% N. NO ACREDITABLE TAX",
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
    map_tax_dict = {
        (8855, 3773, 3794, 3992): "+DIOT: Refunds 8% N.",
        (1640, 2221, 349, 8854, ): "+DIOT: Refunds 16%",
    }
    for account_ids, tag_name in map_tax_dict.items():
        tag = env['account.account.tag'].search([('name', '=', tag_name)], limit=1)
        env.cr.execute("SELECT move_id FROM account_move_line WHERE account_id IN %(account_ids)s AND tax_tag_invert = true;", {
            'account_ids': tuple(account_ids),
        })
        move_ids = [x[0] for x in env.cr.fetchall()]
        env.cr.execute("""
            UPDATE account_move_line
            SET tax_tag_invert = true
            WHERE
                move_id IN %(move_ids)s
                AND tax_tag_invert = false
                AND account_id IN %(account_ids)s;
            """, {
            'move_ids': tuple(move_ids),
            'account_ids': tuple(account_ids),
        })
        env.cr.execute("SELECT id FROM account_move_line WHERE account_id IN %(account_ids)s AND tax_tag_invert = true;", {
            'account_ids': tuple(account_ids),
        })
        aml_ids = [x[0] for x in env.cr.fetchall()]
        for aml_id in aml_ids:
            env.cr.execute("INSERT INTO account_account_tag_account_move_line_rel (account_move_line_id, account_account_tag_id) VALUES (%(aml_id)s, %(tag_id)s) ON CONFLICT DO NOTHING;", {
                'aml_id': aml_id,
                'tag_id': tag.id,
            })
    map_tax_dict = {
        (90, 126, 43, 676, 723, 760, 164, 174, 183): "+DIOT: Refunds",
    }
    for tax_ids, tag_name in map_tax_dict.items():
        tag = env['account.account.tag'].search([('name', '=', tag_name)], limit=1)
        env.cr.execute("""
            DELETE FROM account_account_tag_account_move_line_rel
            WHERE account_account_tag_id = %(tag_id)s
            AND account_move_line_id IN (
                SELECT account_move_line_id FROM account_move_line_account_tax_rel
                WHERE account_tax_id IN %(tax_ids)s
            );
        """, {
            'tag_id': tag.id,
            'tax_ids': tuple(tax_ids),
        })
    plus_refund_tag = env['account.account.tag'].search([('name', '=', "+DIOT: Retención")], limit=1)
    minus_refund_tag = env['account.account.tag'].search([('name', '=', "-DIOT: Retención")], limit=1)
    env.cr.execute("""
        SELECT aml.id
        FROM account_account_tag_account_move_line_rel as atamlr
        LEFT JOIN account_move_line aml ON aml.id = atamlr.account_move_line_id
        WHERE atamlr.account_account_tag_id = 1230 AND aml.credit > 0;
    """, {
        'plus_refund_tag_id': plus_refund_tag.id,
    })
    aml_ids = [x[0] for x in env.cr.fetchall()]
    env.cr.execute("""
        UPDATE account_account_tag_account_move_line_rel
        SET account_account_tag_id = %(minus_refund_tag_id)s
        WHERE account_account_tag_id = %(plus_refund_tag_id)s
        AND account_move_line_id IN %(aml_ids)s;
    """, {
        'minus_refund_tag_id': minus_refund_tag.id,
        'plus_refund_tag_id': plus_refund_tag.id,
        'aml_ids': tuple(aml_ids),
    })
    env.cr.execute("""
        SELECT aml.id
        FROM account_account_tag_account_move_line_rel as atamlr
        JOIN account_move_line aml ON aml.id = atamlr.account_move_line_id
        WHERE atamlr.account_account_tag_id = %(minus_refund_tag_id)s
        AND aml.debit > 0;
    """, {
        'minus_refund_tag_id': minus_refund_tag.id,
    })
    aml_ids = [x[0] for x in env.cr.fetchall()]
    env.cr.execute("""
        UPDATE account_account_tag_account_move_line_rel
        SET account_account_tag_id = %(plus_refund_tag_id)s
        WHERE account_account_tag_id = %(minus_refund_tag_id)s
        AND account_move_line_id IN %(aml_ids)s;
    """, {
        'plus_refund_tag_id': plus_refund_tag.id,
        'minus_refund_tag_id': minus_refund_tag.id,
        'aml_ids': tuple(aml_ids),
    })


def _fix_caba_journals(env):
    _logger.warning('Fixing Cash Basis journals')
    caba_company_dict = {
        3: 141,
        1: 77,
        6: 216,
        4: 187,
        18: 442,
    }
    for company_id, caba_journal_id in caba_company_dict.items():
        env.cr.execute("""
            UPDATE res_company
            SET tax_cash_basis_journal_id = %(caba_journal_id)s
            WHERE id = %(company_id)s;
        """, {
            'caba_journal_id': caba_journal_id,
            'company_id': company_id,
        })


def _update_leave_allocation(env):
    _logger.warning('Updating leave allocation')
    year_days_dict = {
        1: 12,
        2: 14,
        3: 16,
        4: 18,
        5: 20,
        6: 22,
        7: 22,
        8: 22,
        9: 22,
        10: 22,
        11: 24,
        12: 24,
        13: 24,
        14: 24,
        15: 24,
        16: 26,
        17: 26,
        18: 26,
        19: 26,
        20: 26,
        21: 28,
        22: 28,
        23: 28,
        24: 28,
        25: 28,
        26: 30,
        27: 30,
        28: 30,
        29: 30,
        30: 30,
        31: 32,
    }
    old_year_days_dict = {
        1: 6,
        2: 8,
        3: 10,
        4: 12,
        5: 14,
        6: 14,
        7: 14,
        8: 14,
        9: 14,
        10: 16,
        11: 16,
        12: 16,
        13: 16,
        14: 16,
        15: 18,
        16: 18,
        17: 18,
        18: 18,
        19: 18,
        20: 20,
        21: 20,
        22: 20,
        23: 20,
        24: 20,
        25: 22,
        26: 22,
        27: 22,
        28: 22,
        29: 22,
        30: 24,
        31: 24,
    }

    allocations = env["hr.leave.allocation"].search([])
    records = allocations.mapped("employee_id")
    allocations.write({"state": "confirm"})
    allocations.unlink()
    last_year = datetime.date.today().year - 1

    for rec in records:
        contract = env["hr.contract"].search([("employee_id", "=", rec.id), ("state", "=", "open"), ("company_id", "=", rec.company_id.id)])
        if not contract:
            raise UserError("El empleado debe tener un contrato activo para crear sus vacaciones")
        past_contracts = env["hr.contract"].search([("employee_id", "=", rec.id), ("company_id", "=", rec.company_id.id), ("id", "!=", contract.id)], order="date_end desc")
        for past_contract in past_contracts:
            if not past_contract.date_end:
                continue
            if (contract.date_start - past_contract.date_end).days < 30:
                contract = past_contract
            else:
                continue
        for year, days in year_days_dict.items():
            date_start = contract.date_start + relativedelta(years=year)
            if date_start.year < 2023:
                days = old_year_days_dict.get(year, days)
            allocation = env["hr.leave.allocation"].create({
                "name": f"{rec.name} - Año {year}",
                "holiday_status_id": rec.company_id.vacation_leave_type.id,
                "allocation_type": "regular",
                "date_from": date_start,
                "date_to": date_start + relativedelta(years=1, months=6) if date_start.year >= last_year else False,
                "number_of_days": days,
                "holiday_type": "employee",
                "employee_id": rec.id,
            })
            allocation.action_validate()
    env.cr.execute("DELETE FROM hr_leave WHERE id IN (77, 30, 29, 34);")
    leave_list = [
        (21, "2022-07-20 18:00:00", "2022-04-22 08:00:00"),
        (5, "2022-11-11 18:00:00", "2022-08-23 08:00:00"),
        (4, "2023-05-01 18:00:00", "2022-10-28 08:00:00"),
        (15, "2022-12-22 18:00:00", "2022-11-07 08:00:00"),
        (12, "2023-01-24 18:00:00", "2022-12-23 08:00:00"),
        (9, "2023-02-06 11:00:00", "2023-01-04 01:00:00"),
        (11, "2023-03-06 11:00:00", "2023-01-11 01:00:00"),
        (8, "2023-03-22 18:00:00", "2023-01-12 08:00:00"),
        (7, "2023-06-19 18:00:00", "2023-03-09 08:00:00"),
        (1, "2023-07-24 18:00:00", "2023-03-20 08:00:00"),
        (6, "2023-06-20 18:00:00", "2023-05-26 08:00:00"),
        (65, "2023-11-06 18:00:00", "2023-10-18 08:00:00"),
        (18, "2023-12-25 17:00:00", "2023-12-14 07:00:00"),
        (63, "2024-03-29 18:00:00", "2023-12-27 08:00:00"),
        (31, "2024-02-27 18:00:00", "2024-01-23 08:00:00"),
        (22, "2024-04-07 18:00:00", "2024-03-05 08:00:00"),
        (26, "2024-06-06 18:00:00", "2024-03-21 08:00:00"),
        (62, "2024-11-30 18:00:00", "2024-06-25 08:00:00"),
        (64, "2024-12-31 11:00:00", "2024-08-27 02:00:00"),
        (106, "2023-09-14 17:00:00", "2023-08-24 08:00:00"),
    ]
    for id, date_to, date_from in leave_list:
        env.cr.execute("""
            UPDATE hr_leave
            SET
                date_to = %(date_to)s,
                date_from = %(date_from)s,
                request_date_from = %(date_from)s,
                request_date_to = %(date_to)s,
                private_name = CONCAT(private_name, ' (Ajuste a fecha 10/oct/2025)')
            WHERE id = %(id)s;
        """, {
            'id': id,
            'date_to': date_to,
            'date_from': date_from,
        })
        env["hr.leave"].browse(id)._compute_duration()

def _fix_tax_sat_type(env):
    _logger.warning('Fixing tax SAT types')
    tax_mapping = [
        ("IEPS 8% VENTAS", "ieps"),
        ("16% Ventas", "iva"),
        ("16% Compras No Deducibles", "iva"),
        ("IVA(16%) VENTAS", "iva"),
        ("16% Compras", "iva"),
        ("IVA Compras Exentas", "iva"),
        ("IVA Compras 0%", "iva"),
        ("RET ISR HONORARIOS 10%", "isr"),
        ("RET IVA FLETES 4%", "iva"),
        ("RET ISR ARRENDAMIENTO 10%", "isr"),
        ("RETENCION IVA HONORARIOS 10.67%", "iva"),
        ("RETENCION IVA ARRENDAMIENTO 10.67%", "iva"),
        ("ISH 3%", "local"),
        ("ISH 2.5%", "local"),
        ("IVA(0%) COMPRAS", "iva"),
        ("IVA(16%) COMPRAS", "iva"),
        ("IVA Compras Exento", "iva"),
        ("3% ISH", "local"),
        ("2.5% ISH", "local"),
        ("4% Estatal", "local"),
        ("IEPS 8%", "ieps"),
        ("ISH 4.16%", "local"),
        ("IVA Ventas 8%", "iva"),
        ("IVA Compras 8%", "iva"),
        ("IVA Compras 8% No Deducibles", "iva"),
        ("RETENCION IVA 5.33% ", "iva"),
        ("ISH 4%", "local"),
        ("ISH 2.8%", "local"),
        ("ISH 3.5%", "local"),
        ("ISH 2%", "local"),
        ("IUIH 1%", "local"),
        ("ISH 3.75%", "local"),
        ("RET ISR PAGOS EXTRANJERO 10%", "isr"),
        ("RET IVA 6%", "iva"),
        ("RET IVA 3%", "iva"),
        ("ISH 5%", "local"),
        ("IVA Compras 16% No Deducibles", "iva"),
        ("RET LOCAL 5 AL MILLAR", "local"),
        ("IVA Ventas 0%", "iva"),
        ("RET ISR RESICOS 1.25%", "isr"),
        ("RET ISR Ventas Extranjeros 15%", "isr"),
        ("16% Compras Importacion", "iva"),
        ("IEPS 8% COMPRAS", "ieps"),
        ("IEPS 25% VENTAS", "ieps"),
        ("IVA Exento", "iva"),
        ("IEPS 25% COMPRAS", "ieps"),
        ("IEPS 26.5% VENTAS", "ieps"),
        ("IEPS 26.5% COMPRAS", "ieps"),
        ("IEPS 30% VENTAS", "ieps"),
        ("IEPS 30% COMPRAS", "ieps"),
        ("IEPS 53% VENTAS", "ieps"),
        ("IEPS 53% COMPRAS", "ieps"),
        ("ISH 4.2%", "local"),
        ("RET IVA ARRENDAMIENTO 10%", "iva"),
        ("1.25% WH", "isr"),
        ("RET IVA ARRENDAMIENTO 10.67%", "iva"),
        ("RET IVA HONORARIOS 10.67%", "iva"),
        ("IVA 0% VENTAS", "iva"),
        ("IVA 16% VENTAS", "iva"),
        ("IVA 0% COMPRAS", "iva"),
        ("IVA 8% N. COMPRAS", "iva"),
        ("IVA 8% VENTAS", "iva"),
        ("16% NO ACREDITABLE", "iva"),
        ("[old] 16% IMPORTS", "iva"),
        ("[old] 16% IMPORTS INTANGIBLES", "iva"),
        ("Exento", "iva"),
        ("[old] IVA 8% S. COMPRAS", "iva"),
        ("16% IMP", "iva"),
        ("16% IMP INT", "iva"),
        ("8% S.", "iva"),
    ]
    for tax_name, sat_type in tax_mapping:
        env["account.tax"].search([("name", "=", tax_name)]).write({"l10n_mx_tax_type": sat_type})


def _reset_templates(env, templates_to_reset):
    _logger.warning('Resetting templates')
    for template_xml_id in templates_to_reset:
        template = env.ref(template_xml_id, raise_if_not_found=False)
        if template:
            try:
                template.reset_template()
            except Exception as e:
                _logger.warning(f'Error resetting template {template_xml_id}: {e}')
        else:
            _logger.warning(f'Template {template_xml_id} not found')

def _delete_custom_financial_reports(env):
    _logger.warning('Deleting custom financial reports')
    report_ids = (9, 8)
    env.cr.execute("DELETE FROM account_report WHERE id IN %(report_ids)s;", {
        'report_ids': report_ids,
    })
    menu_ids = (1083, 1094, 1093)
    env.cr.execute("DELETE FROM ir_ui_menu WHERE id IN %(menu_ids)s;", {
        'menu_ids': menu_ids,
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
    if templates_to_reset:
        _reset_templates(env, templates_to_reset)
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
    env.cr.execute("UPDATE ir_config_parameter SET key = '8436,8445' WHERE key = 'allowed_non_result_account_ids';")
    _process_edi_files(env)
    _process_diot_fix(env)
    _fix_caba_journals(env)
    _archive_jornals(env)
    _update_leave_allocation(env)
    _delete_custom_financial_reports(env)
    _fix_tax_sat_type(env)
    _logger.warning("Remove usage p01 from purchase orders")
    env.cr.execute("update purchase_order set l10n_mx_edi_usage = null where l10n_mx_edi_usage = 'P01';")
    _logger.warning("Set analytic decimal percentage to 10")
    env.ref("analytic.decimal_percentage_analytic").write({"digits": 10})
    _logger.warning("Set Folio Fiscal in account.move")
    env.cr.execute("UPDATE account_move SET l10n_mx_edi_cfdi_uuid = x_folio_fiscal WHERE x_folio_fiscal IS NOT NULL;")
    _logger.warning("Set filter_hide_0_lines to by_default in all account.report")
    env["account.report"].search([]).write({"filter_hide_0_lines": "by_default"})
    _logger.warning("Set l10n_mx_edi_decimal_places to 6 in USD and MXN")
    env.ref("base.MXN").write({"l10n_mx_edi_decimal_places": 6})
    env.ref("base.USD").write({"l10n_mx_edi_decimal_places": 6})
    _logger.warning("Delete payment term lines with 0 amount")
    env.cr.execute("DELETE FROM account_payment_term_line WHERE value_amount = 0 AND value = 'fixed' AND nb_days = 0;")
    _logger.warning('The migration has finished')
