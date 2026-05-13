import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Truck(Document):
    def validate(self):
        if self.license_end_date and getdate(self.license_end_date) < getdate(today()):
            frappe.msgprint(
                _("انتهاء ترخيص الشاحنة مسجّل كمنقضٍ."),
                indicator="red",
                title=_("الترخيص"),
            )
        if self.insurance_end_date and getdate(self.insurance_end_date) < getdate(today()):
            frappe.msgprint(
                _("انتهاء التأمين مسجّل كمنقضٍ."),
                indicator="orange",
                title=_("التأمين"),
            )
