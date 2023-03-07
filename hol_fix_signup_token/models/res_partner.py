# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=W0622

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    signup_token = fields.Char(copy=False, groups="base.group_user")
    signup_type = fields.Char(
        string="Signup Token Type", copy=False, groups="base.group_user"
    )
    signup_expiration = fields.Datetime(copy=False, groups="base.group_user")
