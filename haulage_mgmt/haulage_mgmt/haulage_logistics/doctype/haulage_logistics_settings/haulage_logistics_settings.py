import frappe
from frappe import _
from frappe.model.document import Document


class HaulageLogisticsSettings(Document):
    def validate(self):
        if self.trip_expense_credit_account:
            root = frappe.db.get_value("Account", self.trip_expense_credit_account, "root_type")
            if root == "Expense":
                frappe.throw(
                    _("حساب «الدائن لترحيل المصروفات» لا يجب أن يكون من نوع مصروف.")
                )
