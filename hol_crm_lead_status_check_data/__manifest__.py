# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "HOL CRM Lead Status Check",
    "version": "11.0.1.0.0",
    "category": "CRM",
    "license": "AGPL-3",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "depends": [
        "crm_lead_status_check",
        "hol_partner_contact_department_data",
        "partner_employee_quantity",
        "partner_contact_job_position",
    ],
    "data": [
        "data/crm_status_check_item_data.xml",
    ],
    "installable": True,
    "auto_install": False,
}
