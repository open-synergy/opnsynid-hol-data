# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import stripe

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    stripe_id = fields.Char(
        string="Stripe ID",
        copy=False,
    )

    @api.model
    def _requirement_fields(self):
        result = [
            "name",
            "email",
        ]
        return result

    @api.multi
    def _check_requirement_fields(self):
        self.ensure_one()
        fields = self._requirement_fields()

        for field in fields:
            checked = getattr(self, field)
            if not checked:
                msg_err = _("Field '%s' must be filled.") % field
                raise UserError(msg_err)

    @api.multi
    def action_create_stripe_id(self):
        for record in self:
            record._create_stripe_id()

    @api.multi
    def _create_stripe_id(self):
        self.ensure_one()
        stripe.api_key = self.env.user.company_id.stripe_api_key
        self._check_requirement_fields()
        result = stripe.Customer.create(
            description=self.name,
            email=self.email,
        )
        self.write(
            {
                "stripe_id": result["id"],
            }
        )
