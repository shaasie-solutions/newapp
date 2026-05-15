import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Driver(Document):
    def validate(self):
        if not (self.full_name or "").strip():
            frappe.throw(_("Driver name is required."))
        self.full_name = self.full_name.strip()
        if self.license_expiry and getdate(self.license_expiry) < getdate(today()):
            frappe.msgprint(
                _("Driver license appears expired or past."),
                indicator="red",
                title=_("Driver license"),
            )
