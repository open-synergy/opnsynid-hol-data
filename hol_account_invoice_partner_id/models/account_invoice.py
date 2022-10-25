# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    partner_database_id = fields.Integer(
        string="Partner Database ID",
        related="partner_id.commercial_partner_id.id",
        store=True,
    )
