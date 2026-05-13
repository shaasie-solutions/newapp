import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class ShippingRequest(Document):
    def validate(self):
        if self.required_loading_date and self.expected_delivery_date:
            if getdate(self.expected_delivery_date) < getdate(self.required_loading_date):
                frappe.throw(
                    _("تاريخ التسليم المتوقع لا يمكن أن يسبق تاريخ التحميل المطلوب.")
                )
