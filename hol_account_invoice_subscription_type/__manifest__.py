# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HOL Subscription Type on Invoice",
    "version": "11.0.1.2.0",
    "license": "AGPL-3",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "subscription_payment_schedule",
        "subscription_hierarchy",
    ],
    "data": [
        "views/account_invoice_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
