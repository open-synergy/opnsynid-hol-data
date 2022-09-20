# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import stripe

from odoo import api, models

endpoint_secret = (
    "whsec_d3632cf8b73770372fe13c2c8877f493ede309ae8e5ea3ac50bf5a4349c992e8"
)


class Webhook(models.Model):
    _name = "webhook"
    _inherit = "webhook"

    @api.multi
    def run_webhook_stripe_all_event(self):
        self.ensure_one()

        payload = self.env.request.jsonrequest["data"]
        sig_header = self.env.request.httprequest.environ["HTTP_STRIPE_SIGNATURE"]
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

        # Handle event
        if event and event["type"] == "payment_intent.succeeded":
            pass
        else:
            # Unexpected event type
            pass
