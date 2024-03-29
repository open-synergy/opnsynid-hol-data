# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Klik Pajak Integration",
    "version": "11.0.1.0.4",
    "license": "LGPL-3",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "hol_efaktur",
        "configuration_helper",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/account_invoice_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
