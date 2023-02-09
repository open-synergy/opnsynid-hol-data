# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class GeneralLedgerXslx(models.AbstractModel):
    _inherit = "report.a_f_r.report_general_ledger_xlsx"

    def _get_report_columns(self, report):
        res = {
            0: {"header": _("Date"), "field": "date", "width": 11},
            1: {"header": _("Entry"), "field": "entry", "width": 18},
            2: {"header": _("Journal"), "field": "journal", "width": 8},
            3: {"header": _("Account"), "field": "account", "width": 9},
            4: {
                "header": _("Product"),
                "field": "product_id",
                "format_align": "left",
                "type": "many2one",
                "width": 18,
            },
            5: {"header": _("Taxes"), "field": "taxes_description", "width": 15},
            6: {"header": _("Partner"), "field": "partner", "width": 25},
            7: {"header": _("Ref - Label"), "field": "label", "width": 40},
            8: {"header": _("Cost center"), "field": "cost_center", "width": 15},
            9: {"header": _("Tags"), "field": "tags", "width": 10},
            10: {"header": _("Rec."), "field": "matching_number", "width": 5},
            11: {
                "header": _("Debit"),
                "field": "debit",
                "field_initial_balance": "initial_debit",
                "field_final_balance": "final_debit",
                "type": "amount",
                "width": 14,
            },
            12: {
                "header": _("Credit"),
                "field": "credit",
                "field_initial_balance": "initial_credit",
                "field_final_balance": "final_credit",
                "type": "amount",
                "width": 14,
            },
            13: {
                "header": _("Cumul. Bal."),
                "field": "cumul_balance",
                "field_initial_balance": "initial_balance",
                "field_final_balance": "final_balance",
                "type": "amount",
                "width": 14,
            },
        }
        if report.foreign_currency:
            foreign_currency = {
                14: {
                    "header": _("Cur."),
                    "field": "currency_id",
                    "field_currency_balance": "currency_id",
                    "type": "many2one",
                    "width": 7,
                },
                15: {
                    "header": _("Amount cur."),
                    "field": "amount_currency",
                    "field_initial_balance": "initial_balance_foreign_currency",
                    "field_final_balance": "final_balance_foreign_currency",
                    "type": "amount_currency",
                    "width": 14,
                },
            }
            res = {**res, **foreign_currency}
        return res

    def write_line(self, line_object):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        for col_pos, column in self.columns.items():
            value = getattr(line_object, column["field"])
            cell_type = column.get("type", "string")
            if cell_type == "many2one":
                if column.get("format_align") == "left":
                    self.sheet.write_string(
                        self.row_pos, col_pos, value.name or "", self.format_left
                    )
                else:
                    self.sheet.write_string(
                        self.row_pos, col_pos, value.name or "", self.format_right
                    )
            elif cell_type == "string":
                if (
                    hasattr(line_object, "account_group_id")
                    and line_object.account_group_id
                ):
                    self.sheet.write_string(
                        self.row_pos, col_pos, value or "", self.format_bold
                    )
                else:
                    self.sheet.write_string(self.row_pos, col_pos, value or "")
            elif cell_type == "amount":
                if (
                    hasattr(line_object, "account_group_id")
                    and line_object.account_group_id
                ):
                    cell_format = self.format_amount_bold
                else:
                    cell_format = self.format_amount
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), cell_format
                )
            elif cell_type == "amount_currency":
                if line_object.currency_id:
                    format_amt = self._get_currency_amt_format(line_object)
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), format_amt
                    )
        self.row_pos += 1
