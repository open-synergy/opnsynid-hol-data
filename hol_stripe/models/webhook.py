# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

import requests
import stripe

from odoo import api, models

_logger = logging.getLogger(__name__)


endpoint_secret = "we_1LkO6qHpeSTSgATaViMLkbSF"


class Webhook(models.Model):
    _name = "webhook"
    _inherit = "webhook"

    @api.multi
    def run_webhook_stripe_all_event(self):
        self.ensure_one()
        payload = self.env.request.jsonrequest
        event = None
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
            payment_intent = event.data.object
            _logger.warning("PaymentIntent was successful!")
            _logger.warning("Data %s", payment_intent["invoice"])
        elif event.type == "payment_method.attached":
            payment_method = event.data.object
            _logger.warning("PaymentMethod was attached to a Customer!")
            _logger.warning("Data %s", payment_method)
        else:
            _logger.warning("Unhandled event type %s", event.type)
