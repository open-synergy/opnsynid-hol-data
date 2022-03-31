# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HOL E-Faktur",
    "version": "11.0.1.0.1",
    "license": "AGPL-3",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "l10n_id_taxform_faktur_pajak_common",
        "partner_company_legal_name",
    ],
    "data": [
        "data/ir_actions_server_data.xml",
    ],
    "installable": True,
    "auto_install": False,
}
