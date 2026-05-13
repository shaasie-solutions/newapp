import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Driver(Document):
    def validate(self):
        if self.license_expiry and getdate(self.license_expiry) < getdate(today()):
            frappe.msgprint(
                _("تاريخ انتهاء رخصة القيادة منتهٍ أو منقضٍ."),
                indicator="red",
                title=_("رخصة السائق"),
            )
