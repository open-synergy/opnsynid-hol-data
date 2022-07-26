# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622

from odoo import api, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    @api.multi
    def _prepare_klikpajak_json_data(self):
        self.ensure_one()
        return {
            "name": self.commercial_partner_id.legal_name,
            "npwp": self.commercial_partner_id.vat,
            "address": self._klikpajak_get_alamat(),
        }

    @api.multi
    def _klikpajak_get_alamat(self):
        self.ensure_one()
        street = self.street or ""
        street2 = self.street2 or ""
        city = self.city or ""
        zip = self.zip or ""
        alamat = street + ". " + street2 + ". " + city + ". " + zip
        return alamat
