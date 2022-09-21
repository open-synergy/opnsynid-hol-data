# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import stripe

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    stripe_id = fields.Char(
        string="Stripe ID",
        readonly=True,
        copy=False,
    )
    stripe_hosted_invoice_url = fields.Char(
        string="Stripe Hosted Invoice URL",
        readonly=True,
        copy=False,
    )

    @api.multi
    def action_create_stripe_id(self):
        for record in self:
            if record.state != "open":
                msgError = _("Stripe can only be created when state is 'OPEN'!")
                raise UserError(msgError)
            record._create_stripe_id()

    @api.multi
    def action_cancel_stripe_id(self):
        for record in self:
            record._cancel_stripe_id()

    @api.multi
    def _cancel_stripe_id(self):
        self.ensure_one()
        stripe.api_key = self.env.user.company_id.stripe_api_key
        stripe.Invoice.void_invoice(
            self.stripe_id,
        )
        self.write(
            {
                "stripe_id": False,
                "stripe_hosted_invoice_url": False,
            }
        )

    @api.multi
    def _create_stripe_id(self):
        self.ensure_one()
        invoice_lines = []
        stripe.api_key = self.env.user.company_id.stripe_api_key
        index = 0
        for invoice_line in self.invoice_line_ids:
            if invoice_line.price_unit > 0:
                invoice_lines.append(invoice_line._prepare_stripe_line_data())
                index += 1
            else:
                previous_index = index - 1
                invoice_lines[previous_index].update(
                    invoice_line._get_stripe_line_discount()
                )

        for line in invoice_lines:
            stripe.InvoiceItem.create(
                unit_amount=line["unit_amount"],
                currency=line["currency"],
                customer=line["customer"],
                description=line["description"],
                quantity=line["quantity"],
                tax_rates=line["tax_rates"],
            )
        result = stripe.Invoice.create(
            customer=self.partner_id.commercial_partner_id.stripe_id,
            collection_method="send_invoice",
            # TODO
            # due_date=self.date_due,
            days_until_due=7,
            payment_settings={
                # TODO: Change into customer balance
                "payment_method_types": ["id_bank_transfer"],
            },
        )
        result = stripe.Invoice.finalize_invoice(result["id"])
        self.write(
            {
                "stripe_id": result["id"],
                "stripe_hosted_invoice_url": result["hosted_invoice_url"],
            }
        )
