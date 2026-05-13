import frappe
from frappe import _
from frappe.model.document import Document


class ShipmentPreparation(Document):
    def validate(self):
        others = frappe.get_all(
            "Shipment Preparation",
            filters={"shipping_request": self.shipping_request},
            pluck="name",
        )
        conflict = [n for n in others if n != self.name]
        if conflict:
            frappe.throw(_("يوجد سجل تجهيز آخر لنفس طلب الشحن."))


def sync_shipping_request_status(doc, method=None):
    if getattr(doc, "doctype", None) != "Shipment Preparation" or not doc.shipping_request:
        return
    if doc.preparation_status == "Ready for Trip" and doc.cargo_prepared:
        cur = frappe.db.get_value("Shipping Request", doc.shipping_request, "request_status")
        if cur == "New":
            frappe.db.set_value(
                "Shipping Request",
                doc.shipping_request,
                "request_status",
                "Goods Prepared",
            )
