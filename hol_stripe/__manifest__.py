# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Stripe Integration",
    "version": "11.0.1.2.2",
    "license": "LGPL-3",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "account",
        "configuration_helper",
        "webhook",
    ],
    "external_dependencies": {
        "python": [
            "stripe",
        ],
    },
    "data": [
        "data/webhook_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/account_tax_views.xml",
        "views/account_invoice_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
