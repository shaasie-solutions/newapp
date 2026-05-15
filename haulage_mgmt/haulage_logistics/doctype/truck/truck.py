import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Truck(Document):
    def validate(self):
        if not (self.truck_name or "").strip():
            frappe.throw(_("Truck name is required."))
        self.truck_name = self.truck_name.strip()
        if self.license_end_date and getdate(self.license_end_date) < getdate(today()):
            frappe.msgprint(
                _("Truck license appears expired."),
                indicator="red",
                title=_("License"),
            )
        if self.insurance_end_date and getdate(self.insurance_end_date) < getdate(today()):
            frappe.msgprint(
                _("Truck insurance appears expired."),
                indicator="orange",
                title=_("Insurance"),
            )
