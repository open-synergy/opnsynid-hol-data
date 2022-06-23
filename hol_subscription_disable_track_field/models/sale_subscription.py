# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _inherit = "sale.subscription"

    name = fields.Char(
        track_visibility=False,
    )
    code = fields.Char(
        track_visibility=False,
    )
    state = fields.Selection(
        track_visibility=False,
    )
    date = fields.Date(
        track_visibility=False,
    )
    recurring_total = fields.Float(
        track_visibility=False,
    )
    recurring_interval = fields.Integer(
        track_visibility=False,
    )
    recurring_rule_type = fields.Selection(
        track_visibility=False,
    )
    close_reason_id = fields.Many2one(
        track_visibility=False,
    )
    template_id = fields.Many2one(
        track_visibility=False,
    )
    user_id = fields.Many2one(
        track_visibility=False,
    )
