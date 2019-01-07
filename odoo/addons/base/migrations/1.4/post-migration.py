# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env['ir.module.module'].update_list()
    # Rename module helpdesk_open_ticket -> helpdesk_task_automation
    env['ir.module.module'].search(
        [('name', '=', 'helpdesk_task_automation')]).unlink()
    openupgrade.update_module_names(
        env.cr, [('helpdesk_open_ticket', 'helpdesk_task_automation')])
    # Rename module helpdesk_close_tickets -> helpdesk_task_automation
    env['ir.module.module'].search(
        [('name', '=', 'helpdesk_task_automation')]).unlink()
    openupgrade.update_module_names(
        env.cr, [('helpdesk_close_tickets', 'helpdesk_task_automation')])
    # Rename module helpdesk_task -> helpdesk_task_automation
    env['ir.module.module'].search(
        [('name', '=', 'helpdesk_task_automation')]).unlink()
    openupgrade.update_module_names(
        env.cr, [('helpdesk_task', 'helpdesk_task_automation')])
    # Rename module helpdesk_merge_tickets -> helpdesk_ticket_merge
    env['ir.module.module'].search(
        [('name', '=', 'helpdesk_ticket_merge')]).unlink()
    openupgrade.update_module_names(
        env.cr, [('helpdesk_merge_tickets', 'helpdesk_ticket_merge')])
    # Rename module crm_new_lead -> helpdesk_ticket_to_lead
    env['ir.module.module'].search(
        [('name', '=', 'helpdesk_ticket_to_lead')]).unlink()
    openupgrade.update_module_names(
        env.cr, [('crm_new_lead', 'helpdesk_ticket_to_lead')])
