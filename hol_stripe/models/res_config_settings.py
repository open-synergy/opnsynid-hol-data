# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from .res_company import ResCompany


class KlikPajaksettings(models.TransientModel):
    _name = "res.config.settings"
    _inherit = ["res.config.settings", "abstract.config.settings"]
    _companyObject = ResCompany
    _prefix = "stripe_"

    stripe_api_key = fields.Char(
        string="Stripe API Key",
        related="company_id.stripe_api_key",
    )
    stripe_endpoint_secret = fields.Char(
        string="Stripe Endpoint Secret",
        related="company_id.stripe_endpoint_secret",
    )
    stripe_journal_id = fields.Many2one(
        string="Stripe Journal",
        comodel_name="account.journal",
        related="company_id.stripe_journal_id",
    )
