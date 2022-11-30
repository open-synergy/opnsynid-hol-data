# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622


from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    invoice_segmentation_ok = fields.Boolean(
        string="Invoice Segmentation Report",
        default=False,
    )
