# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class GeneralLedgerReportMoveLine(models.TransientModel):
    _inherit = "report_general_ledger_move_line"

    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
    )
