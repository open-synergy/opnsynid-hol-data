# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622


from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _name = "account.invoice"

    @api.depends(
        "source_document_res_id",
        "source_document_model_id",
    )
    def _compute_subscription_type(self):
        for record in self:
            if not record.source_document_id:
                result = "invalid"
            else:
                if record.source_document_model == "sale.subscription":
                    result = record.source_document_id.type
                else:
                    result = "invalid"
            record.subscription_type = result

    subscription_type = fields.Selection(
        string="Subscription Type",
        selection=[
            ("invalid", "Not a Subscription Invoice"),
            ("new", "New Subscription"),
            ("renewal", "Renewal"),
            ("upgrade", "Upgrade"),
            ("downgrade", "Downgrade"),
        ],
        compute="_compute_subscription_type",
        store=True,
    )
