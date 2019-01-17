# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.warning('Removing bank accounts with no partner')
    cr.execute('DELETE FROM res_partner_bank WHERE partner_id IS NULL;')
    # cr.execute("UPDATE res_lang SET active = 'f' WHERE iso_code = 'es_MX';")
    # cr.execute("UPDATE res_partner SET  lang = 'en_US';")
