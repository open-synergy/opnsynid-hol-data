# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class ReportInvoiceSegmentation(models.Model):
    _name = "report.invoice_segmentation"
    _auto = False

    invoice_date = fields.Date(
        string="Date",
    )
    invoice_number = fields.Char(
        string="Invoice Number",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
    )
    reference = fields.Text(
        string="Reference",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )
    gross_amount = fields.Float(
        string="Gross Amount",
    )
    subscription_type = fields.Selection(
        string="Subscription Type",
        selection=[
            ("invalid", "Not a Subscription Invoice"),
            ("new", "New Subscription"),
            ("renewal", "Renewal"),
            ("upgrade", "Upgrade"),
            ("downgrade", "Downgrade"),
        ],
    )

    def _select(self):
        select_str = """
        SELECT
            a.id as id,
            b.date AS invoice_date,
            b.name AS invoice_number,
            c.commercial_partner_id AS partner_id,
            '-' AS reference,
            a.product_id AS product_id,
            a.account_id AS account_id,
            (-1.0 * a.balance) AS gross_amount,
            e.subscription_type AS subscription_type
        """
        return select_str

    def _from(self):
        from_str = """
        account_move_line AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE b1.invoice_segmentation_ok = TRUE
        AND d.invoice_segmentation_ok = TRUE
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN account_move AS b ON a.move_id = b.id
        JOIN account_journal AS b1 ON b.journal_id=b1.id
        JOIN res_partner AS c ON a.partner_id = c.id
        JOIN account_account AS d ON a.account_id = d.id
        LEFT JOIN account_invoice AS e ON a.invoice_id = e.id
        """
        return join_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, "report_invoice_segmentation")
        # pylint: disable=locally-disabled, sql-injection
        self._cr.execute(
            """CREATE or REPLACE VIEW report_invoice_segmentation as (
            %s
            FROM %s
            %s
            %s
        )"""
            % (
                self._select(),
                self._from(),
                self._join(),
                self._where(),
            )
        )
