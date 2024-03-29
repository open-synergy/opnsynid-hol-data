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
    stripe_short_io_url = fields.Char(
        string="Short IO URL",
        related="company_id.stripe_short_io_url",
    )
    stripe_short_io_api = fields.Char(
        string="Short IO API Key",
        related="company_id.stripe_short_io_api",
    )
    stripe_short_io_domain = fields.Char(
        string="Short IO Domain",
        related="company_id.stripe_short_io_domain",
    )
    stripe_art_23_id = fields.Many2one(
        string="Stripe Art. 23 Tax",
        comodel_name="account.tax",
        related="company_id.stripe_art_23_id",
    )
