# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError


def _csv_row(data, delimiter=",", quote='"'):
    return (
        quote
        + (quote + delimiter + quote).join(
            [str(x).replace(quote, "\\" + quote) for x in data]
        )
        + quote
        + "\n"
    )


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _prepare_header_1(self):
        header_1 = [
            "FK",
            "KD_JENIS_TRANSAKSI",
            "FG_PENGGANTI",
            "NOMOR_FAKTUR",
            "MASA_PAJAK",
            "TAHUN_PAJAK",
            "TANGGAL_FAKTUR",
            "NPWP",
            "NAMA",
            "ALAMAT_LENGKAP",
            "JUMLAH_DPP",
            "JUMLAH_PPN",
            "JUMLAH_PPNBM",
            "ID_KETERANGAN_TAMBAHAN",
            "FG_UANG_MUKA",
            "UANG_MUKA_DPP",
            "UANG_MUKA_PPN",
            "UANG_MUKA_PPNBM",
            "REFERENSI",
        ]
        return header_1

    @api.multi
    def _prepare_header_2(self):
        header_2 = [
            "LT",
            "NPWP",
            "NAMA",
            "JALAN",
            "BLOK",
            "NOMOR",
            "RT",
            "RW",
            "KECAMATAN",
            "KELURAHAN",
            "KABUPATEN",
            "PROPINSI",
            "KODE_POS",
            "NOMOR_TELEPON",
        ]
        return header_2

    @api.multi
    def _prepare_header_3(self):
        header_3 = [
            "OF",
            "KODE_OBJEK",
            "NAMA",
            "HARGA_SATUAN",
            "JUMLAH_BARANG",
            "HARGA_TOTAL",
            "DISKON",
            "DPP",
            "PPN",
            "TARIF_PPNBM",
            "PPNBM",
        ]
        return header_3

    @api.multi
    def _prepare_data(self):
        self.ensure_one()
        data = {
            "ID_KETERANGAN_TAMBAHAN": "",
            "FG_UANG_MUKA": 0,
            "UANG_MUKA_DPP": 0,
            "UANG_MUKA_PPN": 0,
            "UANG_MUKA_PPNBM": 0,
            "REFERENSI": "",
            "JUMLAH_PPNBM": 0,
            "JALAN": "",
            "NOMOR_TELEPON": "",
            "BLOK": "",
            "NOMOR": "",
            "RT": "",
            "RW": "",
            "KECAMATAN": "",
            "KELURAHAN": "",
            "KABUPATEN": "",
            "PROPINSI": "",
            "KODE_POS": "",
            "JUMLAH_BARANG": 0,
            "TARIF_PPNBM": 0,
            "PPNBM": 0,
        }
        return data

    @api.multi
    def _prepare_attachment_data(self, datas):
        data = {
            "name": "hol_efaktur.csv",
            "datas": datas,
            "datas_fname": "efaktur_%s.csv" % (fields.Datetime.now().replace(" ", "_")),
            "type": "binary",
        }
        return data

    @api.multi
    def _get_alamat(self):
        self.ensure_one()
        street = self.partner_id.commercial_partner_id.street or ""
        street2 = self.partner_id.commercial_partner_id.street2 or ""
        city = self.partner_id.commercial_partner_id.city or ""
        zip = self.partner_id.commercial_partner_id.zip or ""
        alamat = street + ". " + street2 + ". " + city + ". " + zip
        return alamat

    @api.multi
    def _generate_efaktur_invoice(self, delimiter):
        header_1 = self._prepare_header_1()
        header_2 = self._prepare_header_2()
        header_3 = self._prepare_header_3()
        result = "{}{}{}".format(
            _csv_row(header_1, delimiter),
            _csv_row(header_2, delimiter),
            _csv_row(header_3, delimiter),
        )

        for document in self:
            if document.state != "draft":
                data = document._prepare_data()
                no_faktur = (
                    document.enofa_fg_pengganti
                    + document.enofa_jenis_transaksi
                    + document.enofa_nomor_dokumen
                ).replace(".", "")
                alamat_lengkap = document._get_alamat()

                data["KD_JENIS_TRANSAKSI"] = str(document.enofa_jenis_transaksi)
                data["FG_PENGGANTI"] = document.enofa_fg_pengganti
                data["NOMOR_FAKTUR"] = no_faktur
                data["MASA_PAJAK"] = document.enofa_masa_pajak
                data["TAHUN_PAJAK"] = document.enofa_tahun_pajak
                data["TANGGAL_FAKTUR"] = document.enofa_tanggal_dokumen
                data["NPWP"] = document.partner_id.commercial_partner_id.vat
                data["NAMA"] = document.partner_id.commercial_partner_id.legal_name
                data["ALAMAT_LENGKAP"] = alamat_lengkap
                data["JUMLAH_DPP"] = document.enofa_jumlah_dpp
                data["JUMLAH_PPN"] = document.enofa_jumlah_ppn

                header_1_list = ["FK"] + [data[f] for f in header_1[1:]]
                result += _csv_row(header_1_list, delimiter)
                header_2_list = [
                    "FAPR",
                    document.enofa_nama,
                    document.enofa_alamat_lengkap,
                ] + [data[f] for f in header_2[3:]]
                result += _csv_row(header_2_list, delimiter)

                details = []
                for line in document.invoice_line_ids:
                    if line.price_unit > 0:
                        line_dict = {
                            "KODE_OBJEK": line.enofa_kode_objek or "",
                            "NAMA": line.enofa_nama or "",
                            "HARGA_SATUAN": line.enofa_harga_satuan,
                            "JUMLAH_BARANG": line.enofa_jumlah_barang,
                            "HARGA_TOTAL": line.enofa_harga_total,
                            "DPP": int(float(line.enofa_dpp)),
                            "DISKON": 0,
                            "PPN": int(int(float(line.enofa_dpp)) * 0.1),
                            "product_id": line.product_id.id,
                        }
                        details.append(line_dict)
                    else:
                        diskon = line.price_unit * line.quantity
                        dpp = line_dict["DPP"] - abs(diskon)
                        pajak = dpp * 0.1

                        line_dict.update(
                            {
                                "DPP": int(dpp),
                                "DISKON": int(abs(diskon)),
                                "PPN": int(pajak),
                            }
                        )

                for detail in details:
                    header_3_list = (
                        ["OF"] + [str(detail[f]) for f in header_3[1:-2]] + ["0", "0"]
                    )
                    result += _csv_row(header_3_list, delimiter)

        return result

    @api.multi
    def action_generate_efaktur(self):
        obj_ir_attachment = self.env["ir.attachment"]
        if self.filtered(lambda x: x.type != "out_invoice"):
            strWarning = _("Documents are not Customer Invoices")
            raise UserError(strWarning)

        output_head = self._generate_efaktur_invoice(",")
        my_utf8 = output_head.encode("utf-8")
        datas = base64.b64encode(my_utf8)

        criteria = [("name", "=", "hol_efaktur.csv")]
        existing_attachment_id = obj_ir_attachment.search(criteria)

        if existing_attachment_id:
            existing_attachment_id.unlink()

        attachment = obj_ir_attachment.create(self._prepare_attachment_data(datas))

        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % (attachment.id),
            "target": "new",
            "nodedestroy": False,
        }
