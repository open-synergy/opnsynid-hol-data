# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622

import base64
import hashlib
import hmac
import json

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

DICT_TEST_RESPONSE = {
    "code": "00",
    "message": "The Sales Tax Invoice is successfully created",
    "data": {
        "id": 27268,
        "client_reference_id": "INVOICE0000003",
        "approval_status": "DRAFT",
        "invoice_status": "NORMAL",
        "transaction_detail": "01",
        "additional_trx_detail": "",
        "document_number": "020.22.00000004",
        "document_date": "2022-01-15",
        "reference": "TAX0000001",
        "description": "-",
        "total_dpp": 401000000,
        "total_ppn": 40100000,
        "total_ppnbm": 0,
        "total_price": 401000000,
        "total_discount": 0,
        "downpayment_flag": 0,
        "downpayment_dpp": 0,
        "downpayment_ppn": 0,
        "downpayment_ppnbm": 0,
        "items": [
            {
                "name": "item 1",
                "unit_price": 100000,
                "quantity": 10,
                "discount": 0,
                "selling_price": 1000000.00000,
                "dpp": 1000000.00000,
                "ppn": 100000.00000,
                "ppnbm_rate": 0,
                "ppnbm": 0,
            },
            {
                "name": "item2",
                "unit_price": 2000000,
                "quantity": 200,
                "discount": 0,
                "selling_price": 400000000.00000,
                "dpp": 400000000.00000,
                "ppn": 40000000.00000,
                "ppnbm_rate": 0,
                "ppnbm": 0,
            },
        ],
        "customer": {
            "npwp": "12.345.678.9-012.345",
            "nik": "9876543210123456",
            "name": "Customer Name",
            "address": "Customer Address",
            "email": "customer@mail.com",
        },
        "tax_invoice_link": "https://demo.klikpajak.id/public/efaktur/out/"
        + "preview/c5d65f0f-36e6-483c-ac7d-826e086478fc",
        "qr_code": False,
    },
}

JSON_TEST_RESPONSE = json.dumps(DICT_TEST_RESPONSE, indent=4)


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    klikpajak_id = fields.Integer(
        string="Klikpajak ID",
        readonly=True,
    )
    klikpajak_invoice_status = fields.Selection(
        string="Klikpajak Invoice Status",
        selection=[
            ("NORMAL", "Normal"),
            ("NORMAL_SUB", "Substitution"),
            ("SUBSTITUED", "Substituted"),
            ("CANCELLED", "Cancel"),
        ],
        readonly=True,
    )
    klikpajak_approval_status = fields.Selection(
        string="Klikpajak Approval Status",
        selection=[
            ("DRAFT", "Draft"),
            ("APPROVED", "Approved"),
            ("IN_PROGRESS", "In Progress"),
            ("REJECTED", "Reject"),
        ],
        readonly=True,
    )
    klikpajak_cancel_status = fields.Char(
        string="Klikpajak Cancel Status",
        readonly=True,
    )
    klikpajak_qrcode_link = fields.Char(
        string="Klikpajak QRCode Linke",
        readonly=True,
    )
    klikpajak_invoice_link = fields.Char(
        string="Klikpajak Invoice Linke",
        readonly=True,
    )

    @api.multi
    def _prepare_klikpajak_json_data(self):
        self.ensure_one()
        invoice_lines = []
        commercial_part = self.partner_id.commercial_partner_id
        for line in self.invoice_line_ids.filtered(lambda r: r.price_unit > 0):
            invoice_lines.append(line._prepare_klikpajak_json_data())
        return {
            "client_reference_id": self.number,
            "transaction_detail": self.transaction_type_id.code,
            "additional_trx_detail": "00",  # TODO
            "substitution_flag": self._get_substitution_flag(self.fp_state),
            "substituted_faktur_id": None,
            "document_number": self.nomor_seri_id.name,
            "document_date": self.date_taxform,
            "customer": commercial_part._prepare_klikpajak_json_data(),
            "items": invoice_lines,
        }

    @api.multi
    def action_klikpajak_submit_sale_invoice(self):
        for record in self:
            record._klikpajak_submit_sale_invoice()

    @api.multi
    def _get_substitution_flag(self, fp_state):
        self.ensure_one()
        if fp_state == "0":
            return False
        else:
            return True

    @api.multi
    def _get_signature(self):
        self.ensure_one()
        secret = self.company_id.klikpajak_client_secret

        payload = self.company_id._get_klikpajak_signature_header(
            self.company_id.klikpajak_sale_invoice_url, "POST"
        )
        hmac_signature = hmac.new(
            key=secret.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        )
        hmac_digest = hmac_signature.digest()

        signature = base64.b64encode(hmac_digest).decode("utf-8")
        return signature

    @api.multi
    def _get_klikpajak_sale_invoice_header(self):
        self.ensure_one()
        result = self.company_id._get_klikpajak_header()

        signature = self._get_signature()

        authorization = self.company_id._get_klikpajak_authorization_header(signature)
        result.update(
            {
                "Authorization": authorization,
            }
        )
        return result

    @api.multi
    def _klikpajak_submit_sale_invoice(self):
        self.ensure_one()

        headers = self._get_klikpajak_sale_invoice_header()
        params = self.company_id._get_klikpajak_sale_invoice_params()
        json_data = self._prepare_klikpajak_json_data()
        base_url = self.company_id.klikpajak_base_url
        sale_invoice_url = self.company_id.klikpajak_sale_invoice_url
        api_url = base_url + sale_invoice_url

        response = requests.post(
            api_url, params=params, headers=headers, json=json_data
        )

        if response.status_code == "200":
            response_json = json.loads(response.text)
            data = response_json["data"]
            self.write(
                {
                    "klikpajak_id": data["id"],
                    "klikpajak_invoice_status": data["invoice_status"],
                    "klikpajak_cancel_status": data["approval_status"],
                    "klikpajak_qrcode_link": data["qr_code"],
                    "klikpajak_invoice_link": data["tax_invoice_link"],
                }
            )
        else:
            str_error = """Response code: {}

            {}""".format(
                response.status_code,
                response.text,
            )

            raise UserError(str_error)
