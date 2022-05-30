# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from .res_company import ResCompany


class KlikPajaksettings(models.TransientModel):
    _name = "res.config.settings"
    _inherit = ["res.config.settings", "abstract.config.settings"]
    _companyObject = ResCompany
    _prefix = "klikpajak_"

    klikpajak_client_id = fields.Char(
        string="Klik Pajak Client ID",
        related="company_id.klikpajak_client_id",
    )
    klikpajak_client_secret = fields.Char(
        string="Klikpajak Client Secret",
        related="company_id.klikpajak_client_secret",
    )
    klikpajak_base_url = fields.Char(
        string="Klikpajak Base URL",
        related="company_id.klikpajak_base_url",
    )
    klikpajak_sale_invoice_url = fields.Char(
        string="Klikpajak Sale Invoice URL",
        related="company_id.klikpajak_sale_invoice_url",
    )
