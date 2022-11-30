# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HOL Invoice Segmentation Report",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "hol_account_invoice_subscription_type",
    ],
    "data": [
        "security/ir.model.access.csv",
        "reports/segmentation_report.xml",
        "views/account_journal_views.xml",
        "views/account_account_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
