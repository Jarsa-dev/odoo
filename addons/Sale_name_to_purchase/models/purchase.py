# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import string

from odoo import api, fields, models
from odoo.tools.translate import _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            alphabet = list(string.ascii_uppercase)
            alphabet.extend([i + b for i in alphabet for b in alphabet])
            name_purchase = ''
            for letter in alphabet:
                next_code = vals['origin']
                name_purchase = next_code+'-'+str(letter)
                purchase_order = res_partners = self.env['purchase.order'].search(
                    [('name', '=', name_purchase)])
                if not purchase_order:
                    break
            vals['name'] = name_purchase
        return super(PurchaseOrder, self).create(vals)
