# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622

import stripe

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"

    @api.multi
    def _prepare_stripe_line_data(self):
        self.ensure_one()
        return {
            "unit_amount": int(self.price_subtotal / self.quantity) * 100,
            "currency": "idr",
            "customer": self.invoice_id.commercial_partner_id.stripe_id,
            "description": self.name,
            "quantity": int(self.quantity),
            "tax_rates": self._get_stripe_line_tax(),
        }

    @api.multi
    def _get_stripe_line_tax(self):
        self.ensure_one()
        result = []
        invoice_line_tax_ids = self.invoice_line_tax_ids
        if invoice_line_tax_ids:
            stripe_tax_rate_ids = invoice_line_tax_ids.mapped("stripe_id")
            result = stripe_tax_rate_ids
        return result

    @api.multi
    def _get_stripe_line_discount(self):
        self.ensure_one()
        stripe.api_key = self.env.user.company_id.stripe_api_key
        amount = int(abs(self.price_subtotal) / self.quantity) * 100
        coupon = stripe.Coupon.create(
            amount_off=amount,
            duration="once",
            currency="IDR",
        )
        return {"discounts": [{"coupon": coupon["id"]}]}
