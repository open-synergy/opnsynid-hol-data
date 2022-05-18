# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, api, fields, models


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _inherit = "sale.subscription"

    no_schedule_activity_ids = fields.Many2many(
        string="No Schedule Activities",
        comodel_name="mail.activity",
        relation="rel_subscription_2_no_schedule_activity",
        column1="subscription_id",
        column2="activity_id",
    )

    @api.multi
    def action_create_no_schedule_activity(self):
        for record in self:
            record._create_no_schedule_activity()

    @api.multi
    def _create_no_schedule_activity(self):
        self.ensure_one()
        obj_activity = self.env["mail.activity"]
        activity1 = obj_activity.create(
            self._prepare_no_schedule_activity(self.user_id)
        )
        if self.user_id.sale_team_id and self.user_id.sale_team_id.user_id:
            activity2 = obj_activity.create(
                self._prepare_no_schedule_activity(self.user_id.sale_team_id.user_id)
            )
        self.write({"no_schedule_activity_ids": [(6, 0, [activity1.id, activity2.id])]})

    @api.multi
    def _prepare_no_schedule_activity(self, user):
        self.ensure_one()
        return {
            "res_id": self.id,
            "res_model_id": self.env.ref(
                "sale_subscription.model_sale_subscription"
            ).id,
            "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
            "summary": _("Generate payment schedule"),
            "user_id": user.id,
        }

    @api.multi
    def action_cancel_no_schedule_activity(self):
        for record in self:
            record._cancel_no_schedule_activity()

    @api.multi
    def _cancel_no_schedule_activity(self):
        self.ensure_one()
        if self.no_schedule_activity_ids:
            self.no_schedule_activity_ids.action_done()
