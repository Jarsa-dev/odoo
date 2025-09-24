# Copyright 2024 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# List of modules to install
to_install = [
    "hr_timesheet_operating_unit",
    "stock_analytic",
    "l10n_mx_edi_statement_line_payment_method",
    "l10n_mx_edi_account_move_payment_report",
    "queue_job_cron_jobrunner",
    "report_sale_order_mtnmx",
    "l10n_mx_edi_decimal_fix",
]

# List of modules to remove (uninstall)
to_remove = [
]

# List of modules to remove all views.
modules_remove_views = [
]

# List of modules to remove all security rules, access and groups.
modules_remove_security = [
]


# List of strings with XML ID.
records_to_remove = [
    "crm.crm_team_view_kanban_dashboard",
    "sale.crm_team_view_kanban_dashboard",
    "account_operating_unit.view_move_form",
    "account_tax_cash_basis_reference.view_account_move_form",
    "mtnmx.view_l10n_mx_edi_invoice_form_inherit",
    "account_move_tier_validation.view_move_form",
    "l10n_mx_edi_cancellation.view_mx_edi_cancellation_complement_invoice_form",
    "mtnmx.account_bank_statement_tree_customization",
    "mtnmx.product_supplierinfo_tree_view_customization",
    "l10n_mx_edi_cancellation.view_reversal_config_settings",
    "account_analytic_tag_assign.res_company_grupo_bikiya",
    "partner_group.view_partner_form",
    "partner_group.view_res_partner_filter",
    "account_analytic_tag_assign.res_partner_mtnmx",
    "purchase_analytic.purchase_order_view_search_inherit_purchase_analytic",
    "project_parent_task_filter.view_task_kanban_subtask",
    "account_analytic_tag_assign.view_account_analytic_tag_document_report_tree",
    "account_analytic_tag_assign.sale_order_mtnmx_search",
    "mtnmx.purchase_order_tree_customization",
    "studio_customization.odoo_studio_purchase_11accd8a-ac08-473e-98e9-f56b14b0bd60",
    "studio_customization.odoo_studio_purchase_3b2a80c3-f65e-4866-83fd-bcee8bcba527",
    "studio_customization.odoo_studio_purchase_12ba87eb-b877-461d-831e-1e257392ce1c",
]

# List of tuples with the following format
# ('old.model.name', 'new.model.name'),
models_to_rename = [
]

# List of tuples with the following format
# ('old_table_name', 'new_table_name'),
tables_to_rename = [
]

# List of tuples with the following format
# ('model.name', 'table_name', 'old_field', 'new_field'),
fields_to_rename = [
    ("product.product", "product_product", "x_studio_product_review", "product_review"),
]

# List of tuples with the follwing format
# ('old_module_name', 'new_module_name'),
modules_to_rename = [
]

external_ids_to_remove = [
]

assets_to_remove = [
    "/account_analytic_tag_assign/static/src/js/form_widgets.js",
    "/tpv_analytic_account_isolation/static/src/js/tpv_analytic_user_bar.js",
    "/date_range/static/src/js/date_range.js",
    "/report_xlsx/static/src/js/report/action_manager_report.js",
    "/base_tier_validation/static/src/js/systray.js",
    "/base_tier_validation/static/src/js/tier_review_widget.js",
    "/mail_tracking/static/src/js/mail_tracking.js",
    "/mail_tracking/static/src/js/failed_message/discuss.js",
    "/mail_tracking/static/src/js/failed_message/thread.js",
    "/mis_builder/static/src/js/mis_report_widget.js",
    "/l10n_mx_edi_vendor_bills/static/src/js/attach_xmls.js",
    "/web_timeline/static/lib/vis/vis-timeline-graph2d.min.js",
    "/web_timeline/static/src/js/timeline_view.js",
    "/web_timeline/static/src/js/timeline_renderer.js",
    "/web_timeline/static/src/js/timeline_controller.js",
    "/web_timeline/static/src/js/timeline_model.js",
    "/web_timeline/static/src/js/timeline_canvas.js",
    "/web_widget_color/static/lib/jscolor/jscolor.js",
    "/web_widget_color/static/src/js/widget.js",
    "/base_tier_validation/static/src/scss/systray.scss",
    "/base_tier_validation/static/src/scss/review.scss",
    "/mail_tracking/static/src/css/mail_tracking.scss",
    "/mail_tracking/static/src/css/failed_message.scss",
    "/mis_builder/static/src/css/custom.css",
    "/project_timeline/static/src/scss/project_timeline.scss"
]


def rename_modules(env, old, new):
    env['ir.module.module'].update_list()
    _logger.warning(
        'Rename module %s -> %s' % (old, new))
    module = env['ir.module.module'].search(
        [('name', '=', new)])
    old_module = env['ir.module.module'].search(
        [('name', '=', old)])
    module.invalidate_recordset()
    if module and old_module:
        env.cr.execute(
            "DELETE FROM ir_model_data WHERE name = 'module_%s'" % new)
        env.cr.execute(
            'DELETE FROM ir_module_module WHERE id = %s' % module.id)
        openupgrade.update_module_names(env.cr, [(old, new)])


def remove_module_views(env, module_list):
    def recursive_inherit_ids(records):
        env.cr.execute("""
            SELECT id
            FROM ir_ui_view
            WHERE inherit_id IN %(ids)s;
        """, {'ids': tuple(records.mapped('res_id'))})
        res = env.cr.fetchall()
        view_ids = [x[0] for x in res]
        new_records = env['ir.model.data'].search([
            ('model', '=', 'ir.ui.view'),
            ('res_id', 'in', view_ids)
        ])
        new_records |= records
        if len(new_records) == len(records):
            return records
        return recursive_inherit_ids(new_records)
    recs = env['ir.model.data'].search([
        ('model', '=', 'ir.ui.view'),
        ('module', 'in', module_list),
    ])
    records = recursive_inherit_ids(recs)
    return records.mapped('complete_name')


def remove_module_security(env, module_list):
    recs = env['ir.model.data'].search([
        ('model', '=', 'ir.model.access'),
        ('module', 'in', module_list),
    ])
    access = env['ir.model.access'].browse(recs.mapped('res_id'))
    access.unlink()
    recs = env['ir.model.data'].search([
        ('model', '=', 'ir.rule'),
        ('module', 'in', module_list),
    ])
    rules = env['ir.rule'].browse(recs.mapped('res_id'))
    rules.unlink()
    recs = env['ir.model.data'].search([
        ('model', '=', 'res.groups'),
        ('module', 'in', module_list),
    ])
    groups = env['res.groups'].browse(recs.mapped('res_id'))
    access = env['ir.model.access'].search([
        ('group_id', 'in', groups.ids)
    ])
    access.unlink()
    groups.unlink()


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning("Change rounding for currencies")
    env.ref("base.USD").write({"rounding": 0.000001})
    env.ref("base.MXN").write({"rounding": 0.000001})
    if records_to_remove:
        _logger.warning('Delete records from XML ID')
        openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    if modules_remove_views:
        _logger.warning('Remove module views')
        openupgrade.delete_records_safely_by_xml_id(
            env, remove_module_views(env, modules_remove_views))
    if modules_remove_security:
        _logger.warning('Remove module security')
        remove_module_security(env, modules_remove_security)
    if modules_to_rename:
        _logger.warning('Modules to rename')
        for module in modules_to_rename:
            rename_modules(env, module[0], module[1])
    if models_to_rename:
        _logger.warning('Models to rename')
        openupgrade.rename_models(env.cr, models_to_rename)
    if tables_to_rename:
        _logger.warning('Tables to rename')
        openupgrade.rename_tables(env.cr, tables_to_rename)
    if fields_to_rename:
        _logger.warning('Fields to rename')
        openupgrade.rename_fields(env, fields_to_rename)
    if to_install:
        env['ir.module.module'].update_list()
        _logger.warning('Installing new modules')
        modules_to_install = env['ir.module.module'].search([
            ('name', 'in', to_install)])
        modules_to_install.button_install()
    if to_remove:
        _logger.warning('Uninstalling not required modules')
        modules_to_remove = env['ir.module.module'].search([
            ('name', 'in', to_remove)])
        modules_to_remove += modules_to_remove.downstream_dependencies()
        modules_to_remove.module_uninstall()
        modules_to_remove.unlink()
    if external_ids_to_remove:
        _logger.warning('Removing external IDs')
        for external_id in external_ids_to_remove:
            module, external_id = external_id.split('.')
            _logger.warning('Removing external ID: %s.%s', module, external_id)
            env['ir.model.data'].search([
                ('module', '=', module),
                ('name', '=', external_id)
            ]).unlink()
    _logger.warning('Removing ir_config_parameter l10n_mx_partner_blocklist_url_not_located')
    env.cr.execute("DELETE FROM ir_config_parameter WHERE key = 'l10n_mx_partner_blocklist_url_not_located';")
    _logger.warning('Updating res_partner l10n_mx_edi_usage and l10n_mx_edi_supplier_usage from P01 to G03')
    env.cr.execute("UPDATE res_partner SET l10n_mx_edi_usage = 'G03' WHERE l10n_mx_edi_usage = 'P01';")
    env.cr.execute("UPDATE res_partner SET l10n_mx_edi_supplier_usage = 'G03' WHERE l10n_mx_edi_supplier_usage = 'P01';")
    _logger.warning('Remove account_account_account_tag with id 1147 and 1001')
    env.cr.execute("DELETE FROM account_account_account_tag WHERE account_account_tag_id IN (1147, 1001);")
    if assets_to_remove:
        _logger.warning('Removing ir_assets')
        for asset in assets_to_remove:
            _logger.warning('Removing ir_asset for %s', asset)
            env.cr.execute("DELETE FROM ir_asset WHERE path = %(asset)s;", {'asset': asset})
