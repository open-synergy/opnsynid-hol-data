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
    def _webhook_stripe_create_accounting_entry(self, stripe_object):
        self.ensure_one()
        AccountMove = self.env["account.move"]
        try:
            account_move = AccountMove.create(
                self._webhook_stripe_prepare_accounting_entry(stripe_object)
            )
        except Exception as e:
            _logger.warning(e)

        self._webhook_stripe_create_payment(account_move, stripe_object)

        return account_move.id

    @api.multi
    def _webhook_stripe_create_payment(self, account_move, stripe_object):
        self.ensure_one()
        account = self._webhook_stripe_get_credit_account()
        lines = account_move.line_ids.filtered(lambda r: r.account_id.id == account.id)
        criteria = [
            ("stripe_id", "=", stripe_object["invoice"]),
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
                ml = lines + inv_lines
                ml.reconcile()

    @api.multi
    def _webhook_stripe_prepare_accounting_entry(self, stripe_object):
        self.ensure_one()
        lines = []
        lines.append(self._webhook_stripe_prepare_accounting_debit_line(stripe_object))
        lines.append(self._webhook_stripe_prepare_accounting_credit_line(stripe_object))
        return {
            "journal_id": self._webhook_stripe_get_journal().id,
            "date": fields.Date.today(),
            "line_ids": lines,
            "name": "/",
        }

    @api.multi
    def _webhook_stripe_prepare_accounting_debit_line(self, stripe_object):
        self.ensure_one()
        name = "Test Stripe Payment"
        account = self._webhook_stripe_get_debit_account()
        debit = self._webhook_stripe_get_debit_amount(stripe_object)
        return (
            0,
            0,
            {
                "name": name,
                "account_id": account.id,
                "debit": debit / 100.00,
                "credit": 0.0,
            },
        )

    @api.multi
    def _webhook_stripe_prepare_accounting_credit_line(self, stripe_object):
        self.ensure_one()
        name = "Test Stripe Payment"
        account = self._webhook_stripe_get_credit_account()
        credit = self._webhook_stripe_get_credit_amount(stripe_object)
        return (
            0,
            0,
            {
                "name": name,
                "account_id": account.id,
                "debit": 0.0,
                "credit": credit / 100.00,
            },
        )

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
        return stripe_object["amount"]

    @api.multi
    def _webhook_stripe_get_credit_amount(self, stripe_object):
        self.ensure_one()
        return stripe_object["amount"]
