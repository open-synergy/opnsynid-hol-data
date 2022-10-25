# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    _name = "res.company"

    stripe_api_key = fields.Char(
        string="Stripe API Key",
    )
    stripe_endpoint_secret = fields.Char(
        string="Stripe Endpoint Secret",
    )
    stripe_journal_id = fields.Many2one(
        string="Stripe Journal",
        comodel_name="account.journal",
    )
    stripe_short_io_url = fields.Char(
        string="Short IO URL",
    )
    stripe_short_io_api = fields.Char(
        string="Short IO API Key",
    )
    stripe_short_io_domain = fields.Char(
        string="Short IO Domain",
    )
