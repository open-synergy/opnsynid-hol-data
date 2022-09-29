# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622


from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _name = "account.invoice"

    @api.depends(
        "subscription_id",
        "subscription_id.type",
        "subscription_type_method",
        "manual_subscription_type",
    )
    def _compute_subscription_type(self):
        for record in self:
            result = "invalid"
            if (
                record.subscription_type_method == "manual"
                and record.manual_subscription_type
            ):
                result = record.manual_subscription_type
            elif record.subscription_type_method == "auto" and record.subscription_id:
                result = record.subscription_id.type
            record.subscription_type = result

    @api.depends(
        "source_document_res_id",
        "source_document_model_id",
    )
    def _compute_subscription(self):
        for record in self:
            result = False
            if (
                record.source_document_model == "sale.subscription"
                and record.source_document_res_id != 0
            ):
                subscriptions = self.env["sale.subscription"].search(
                    [("id", "=", record.source_document_res_id)]
                )
                if len(subscriptions) > 0:
                    result = subscriptions[0]
            record.subscription_id = result

    subscription_type_method = fields.Selection(
        string="Subscription Type Method",
        selection=[
            ("auto", "Automatic"),
            ("manual", "Manual"),
        ],
        required=True,
        default="auto",
    )
    subscription_id = fields.Many2one(
        string="# Subscription",
        comodel_name="sale.subscription",
        compute="_compute_subscription",
        store=True,
    )
    manual_subscription_type = fields.Selection(
        string="Manual Subscription Type",
        selection=[
            ("new", "New Subscription"),
            ("renewal", "Renewal"),
            ("upgrade", "Upgrade"),
            ("downgrade", "Downgrade"),
        ],
    )
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
