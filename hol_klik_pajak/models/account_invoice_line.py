# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"

    @api.multi
    def _prepare_klikpajak_json_data(self):
        self.ensure_one()
        return {
            "name": self.name,
            "unit_price": self.price_unit,
            "quantity": self.price_unit,
            "discount": self._get_hol_discount(),
            "ppnbm_rate": 0.0,
        }

    @api.multi
    def _get_hol_discount(self):
        self.ensure_one()
        return 0.0
