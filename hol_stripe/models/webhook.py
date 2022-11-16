# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

import requests
import stripe

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Webhook(models.Model):
    _name = "webhook"
    _inherit = "webhook"

    @api.multi
    def run_webhook_stripe_all_event(self):
        self.ensure_one()
        payload = self.env.request.jsonrequest
        event = None
        endpoint_secret = self.env.user.company_id.stripe_endpoint_secret
        try:
            event = stripe.Event.construct_from(payload, endpoint_secret)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (
                401,
                410,
                500,
            ):
                pass
            else:
                raise e

        if event.type == "payment_intent.succeeded":
            stripe_object = event.data.object
            self._webhook_stripe_create_accounting_entry(stripe_object)
        else:
            _logger.warning("Unhandled event type %s", event.type)

    @api.multi
    def _webhook_stripe_cancel_invalid_payment_intent(self, stripe_object):
        self.ensure_one()
        stripe.api_key = self.env.user.company_id.stripe_api_key
        if stripe_object["status"] == "requires_payment_method":
            stripe.PaymentIntent.cancel(stripe_object["id"])

    @api.multi
    def _webhook_stripe_check_pph_23(self, stripe_object):
        self.ensure_one()
        result = False
        criteria = [
            ("state", "=", "open"),
            ("stripe_art_23_id", "=", stripe_object["invoice"]),
        ]
        AccountInvoice = self.env["account.invoice"]
        invoices = AccountInvoice.search(criteria)
        if len(invoices) > 0:
            result = True
        return result

    @api.multi
    def _webhook_get_invoice(self, stripe_object):
        self.ensure_one()
        result = False
        criteria = [
            "&",
            ("state", "=", "open"),
            "|",
            ("stripe_id", "=", stripe_object["invoice"]),
            ("stripe_art_23_id", "=", stripe_object["invoice"]),
        ]
        AccountInvoice = self.env["account.invoice"]
        invoices = AccountInvoice.search(criteria)
        _logger.info(len(invoices))
        if len(invoices) > 0:
            result = invoices[0]
        return result

    @api.multi
    def _webhook_stripe_create_accounting_entry(self, stripe_object):
        self.ensure_one()
        AccountMove = self.env["account.move"]
        stripe.api_key = self.env.user.company_id.stripe_api_key
        try:
            invoice = self._webhook_get_invoice(stripe_object)
            check_pph_23 = self._webhook_stripe_check_pph_23(stripe_object)
            account_move = AccountMove.create(
                self._webhook_stripe_prepare_accounting_entry(
                    stripe_object, invoice, check_pph_23
                )
            )
            account_move.post()
            self._webhook_stripe_create_payment(stripe_object, account_move)
            if check_pph_23:
                stripe.Invoice.void_invoice(invoice.stripe_id)
            else:
                stripe.Invoice.void_invoice(invoice.stripe_art_23_id)

        except Exception as e:
            _logger.warning(e)

    @api.multi
    def _webhook_stripe_create_payment(self, stripe_object, account_move):
        self.ensure_one()
        account = self._webhook_stripe_get_credit_account()
        lines = account_move.line_ids.filtered(lambda r: r.account_id.id == account.id)
        criteria = [
            "&",
            ("state", "=", "open"),
            "|",
            ("stripe_id", "=", stripe_object["invoice"]),
            ("stripe_art_23_id", "=", stripe_object["invoice"]),
        ]
        AccountInvoice = self.env["account.invoice"]
        invoices = AccountInvoice.search(criteria)
        _logger.info(len(invoices))
        if len(invoices) > 0:
            invoice = invoices[0]
            inv_lines = invoice.move_id.line_ids.filtered(
                lambda r: r.account_id.id == account.id
            )
            _logger.info(len(inv_lines))
            if len(inv_lines) > 0:
                ml = inv_lines + lines
                ml.reconcile()

        criteria = [
            "&",
            ("state", "=", "open"),
            "|",
            ("stripe_id", "=", stripe_object["invoice"]),
            ("stripe_art_23_id", "=", stripe_object["invoice"]),
        ]
        AccountInvoice = self.env["account.invoice"]
        invoices = AccountInvoice.search(criteria)
        if len(invoices) > 0:
            invoices[0]._cancel_stripe_id()
            invoices[0]._cancel_stripe_id_with_art_23()

    @api.multi
    def _webhook_stripe_prepare_accounting_entry(
        self, stripe_object, invoice, check_pph_23
    ):
        self.ensure_one()
        lines = []
        lines.append(
            self._webhook_stripe_prepare_accounting_debit_line(stripe_object, invoice)
        )
        lines.append(
            self._webhook_stripe_prepare_accounting_credit_line(
                stripe_object, invoice, check_pph_23
            )
        )
        if check_pph_23:
            lines.append(
                self._webhook_stripe_prepare_accounting_pph_23_line(
                    stripe_object, invoice
                )
            )
        return {
            "journal_id": self._webhook_stripe_get_journal().id,
            "date": fields.Date.today(),
            "line_ids": lines,
            "name": "/",
            "ref": invoice.number,
        }

    @api.multi
    def _webhook_stripe_prepare_accounting_debit_line(self, stripe_object, invoice):
        self.ensure_one()
        name = "Stripe payment for {} invoice number {}".format(
            invoice.partner_id.commercial_partner_id.name,
            invoice.number,
        )
        account = self._webhook_stripe_get_debit_account()
        debit = self._webhook_stripe_get_debit_amount(stripe_object)
        return (
            0,
            0,
            {
                "name": name,
                "account_id": account.id,
                "debit": debit,
                "credit": 0.0,
                "partner_id": invoice.partner_id.commercial_partner_id.id,
            },
        )

    @api.multi
    def _webhook_stripe_prepare_accounting_credit_line(
        self, stripe_object, invoice, check_pph_23
    ):
        self.ensure_one()
        name = "Stripe payment for {} invoice number {}".format(
            invoice.partner_id.commercial_partner_id.name,
            invoice.number,
        )
        account = self._webhook_stripe_get_credit_account()
        credit = self._webhook_stripe_get_credit_amount(
            stripe_object, invoice, check_pph_23
        )
        return (
            0,
            0,
            {
                "name": name,
                "account_id": account.id,
                "debit": 0.0,
                "credit": credit,
                "partner_id": invoice.partner_id.commercial_partner_id.id,
            },
        )

    @api.multi
    def _webhook_stripe_prepare_accounting_pph_23_line(self, stripe_object, invoice):
        self.ensure_one()
        name = "Stripe payment for {} invoice number {}".format(
            invoice.partner_id.commercial_partner_id.name,
            invoice.number,
        )
        account = self._webhook_stripe_get_pph_23_account()
        debit = self._webhook_stripe_get_pph_23_amount(stripe_object, invoice)
        return (
            0,
            0,
            {
                "name": name,
                "account_id": account.id,
                "debit": debit,
                "credit": 0.0,
            },
        )

    @api.multi
    def _webhook_stripe_get_pph_23_account(self):
        self.ensure_one()
        if not self.env.user.company_id.stripe_art_23_id:
            error_mg = _("No stripe PPh 23 tax")
            raise UserError(error_mg)

        return self.env.user.company_id.stripe_art_23_id.account_id

    @api.multi
    def _webhook_stripe_get_debit_account(self):
        self.ensure_one()
        if not self.env.user.company_id.stripe_journal_id:
            error_mg = _("No stripe journal")
            raise UserError(error_mg)

        return self.env.user.company_id.stripe_journal_id.default_debit_account_id

    @api.multi
    def _webhook_stripe_get_credit_account(self):
        self.ensure_one()
        if not self.env.user.company_id.stripe_journal_id:
            error_mg = _("No stripe journal")
            raise UserError(error_mg)

        return self.env.user.company_id.stripe_journal_id.default_credit_account_id

    @api.multi
    def _webhook_stripe_get_journal(self):
        self.ensure_one()
        if not self.env.user.company_id.stripe_journal_id:
            error_mg = _("No stripe journal")
            raise UserError(error_mg)

        return self.env.user.company_id.stripe_journal_id

    @api.multi
    def _webhook_stripe_get_debit_amount(self, stripe_object):
        self.ensure_one()
        return stripe_object["amount"] / 100.0

    @api.multi
    def _webhook_stripe_get_credit_amount(self, stripe_object, invoice, check_pph_23):
        self.ensure_one()
        amount = stripe_object["amount"] / 100.0
        if check_pph_23:
            amount = amount + (invoice.amount_untaxed * 0.02)
        return amount

    @api.multi
    def _webhook_stripe_get_pph_23_amount(self, stripe_object, invoice):
        self.ensure_one()
        return invoice.amount_untaxed * 0.02
