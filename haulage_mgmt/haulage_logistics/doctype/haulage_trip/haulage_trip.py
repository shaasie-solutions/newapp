import frappe
from frappe import _
from frappe.model.document import Document


class HaulageTrip(Document):
    def validate(self):
        if not self.company:
            self.company = frappe.defaults.get_user_default("Company") or frappe.db.get_value(
                "Company", {}, "name"
            )
        if not self.company:
            frappe.throw(_("Set the company on the trip (no default company for the user)."))
        self._validate_shipments_not_empty()
        self._validate_shipments_ready()
        self._validate_route_alignment()
        self._validate_no_duplicate_shipment_on_active_trips()
        self._validate_truck_and_driver()
        self._validate_trip_status_consistency()

    def _validate_shipments_not_empty(self):
        if self.trip_status == "Cancelled":
            return
        if not (self.get("shipments") or []):
            frappe.throw(_("Add at least one shipment to the trip (unless the trip is cancelled)."))
        seen = set()
        for row in self.get("shipments") or []:
            if not row.shipping_request:
                continue
            if row.shipping_request in seen:
                frappe.throw(_("Shipping request {0} is duplicated in the shipment table.").format(row.shipping_request))
            seen.add(row.shipping_request)

    def _validate_shipments_ready(self):
        for row in self.get("shipments") or []:
            if not row.shipping_request:
                continue
            prep = frappe.db.get_value(
                "Shipment Preparation",
                {"shipping_request": row.shipping_request},
                ["name", "preparation_status", "cargo_prepared"],
                as_dict=True,
            )
            if not prep:
                frappe.throw(
                    _("Create a shipment preparation record for {0} before adding it to a trip.").format(
                        row.shipping_request
                    )
                )
            if prep.preparation_status != "Ready for Trip":
                frappe.throw(
                    _("Shipping request {0} is not in Ready for Trip preparation status.").format(
                        row.shipping_request
                    )
                )
            if not prep.cargo_prepared:
                frappe.throw(_("Confirm cargo is prepared for shipping request {0}.").format(row.shipping_request))
            row.shipment_preparation = prep.name

    def _validate_route_alignment(self):
        if not self.shipping_route:
            return
        for row in self.get("shipments") or []:
            if not row.shipping_request:
                continue
            sr_route = frappe.db.get_value(
                "Shipping Request", row.shipping_request, "shipping_route"
            )
            if sr_route and sr_route != self.shipping_route:
                frappe.msgprint(
                    _("Warning: shipping request {0} uses route {1}, which differs from the trip route.").format(
                        row.shipping_request, sr_route
                    ),
                    indicator="orange",
                    title=_("Route mismatch"),
                )

    def _validate_no_duplicate_shipment_on_active_trips(self):
        active_status = ("Preparing", "Started", "Paused")
        if self.trip_status not in active_status:
            return
        for row in self.get("shipments") or []:
            if not row.shipping_request:
                continue
            parents = frappe.get_all(
                "Haulage Trip Shipment",
                filters={"shipping_request": row.shipping_request},
                pluck="parent",
            )
            for parent in parents:
                if self.name and parent == self.name:
                    continue
                trip_status = frappe.db.get_value("Haulage Trip", parent, "trip_status")
                if trip_status in active_status:
                    frappe.throw(
                        _("Shipping request {0} is already on active trip {1}.").format(
                            row.shipping_request, parent
                        )
                    )

    def _validate_truck_and_driver(self):
        if self.trip_status in ("Cancelled", "Completed"):
            return
        if self.driver:
            st = frappe.db.get_value("Driver", self.driver, "driver_status")
            if st and st != "Active" and self.trip_status in ("Started", "Paused", "Preparing"):
                frappe.throw(_("Driver {0} is not Active.").format(self.driver))
        if self.truck:
            st = frappe.db.get_value("Truck", self.truck, "truck_status")
            if st == "Stopped" and self.trip_status != "Cancelled":
                frappe.throw(_("Truck {0} is stopped and cannot be used.").format(self.truck))
            if st == "Maintenance" and self.trip_status in ("Started", "Paused"):
                frappe.throw(_("Truck {0} is under maintenance.").format(self.truck))

    def _validate_trip_status_consistency(self):
        if self.trip_status != "Completed":
            return
        events = [e.event_type for e in (self.get("trip_events") or []) if e.event_type]
        if events and events[-1] != "Return":
            frappe.msgprint(
                _(
                    "Trip is set to Completed but the last event is not Return. Prefer logging Return to close the trip."
                ),
                indicator="orange",
                title=_("Trip event reminder"),
            )


def refresh_truck_fleet_status(truck_name):
    """Set truck Busy when any active trip exists; otherwise Available (respects Maintenance/Stopped)."""
    if not truck_name:
        return
    cur = frappe.db.get_value("Truck", truck_name, "truck_status")
    if cur in ("Maintenance", "Stopped"):
        return
    busy = frappe.db.sql(
        """
        SELECT 1 FROM `tabHaulage Trip`
        WHERE truck = %s AND trip_status IN ('Preparing', 'Started', 'Paused')
        LIMIT 1
        """,
        (truck_name,),
    )
    if busy:
        frappe.db.set_value("Truck", truck_name, "truck_status", "Busy")
    else:
        frappe.db.set_value("Truck", truck_name, "truck_status", "Available")


def on_trip_update(doc, method=None):
    if getattr(doc, "doctype", None) != "Haulage Trip":
        return
    _update_preparations_and_requests(doc)
    refresh_truck_fleet_status(doc.truck)
    prev = doc.get_doc_before_save()
    if prev and prev.truck and prev.truck != doc.truck:
        refresh_truck_fleet_status(prev.truck)


def _update_preparations_and_requests(doc):
    for row in doc.get("shipments") or []:
        if not row.shipping_request:
            continue
        prep_name = row.shipment_preparation or frappe.db.get_value(
            "Shipment Preparation",
            {"shipping_request": row.shipping_request},
            "name",
        )
        if not prep_name:
            continue

        if doc.trip_status == "Cancelled":
            frappe.db.set_value(
                "Shipment Preparation",
                prep_name,
                "preparation_status",
                "Ready for Trip",
            )
            frappe.db.set_value(
                "Shipping Request", row.shipping_request, "request_status", "Goods Prepared"
            )
        elif doc.trip_status == "Preparing":
            frappe.db.set_value(
                "Shipment Preparation",
                prep_name,
                "preparation_status",
                "Ready for Trip",
            )
            frappe.db.set_value(
                "Shipping Request", row.shipping_request, "request_status", "Goods Prepared"
            )
        else:
            frappe.db.set_value(
                "Shipment Preparation",
                prep_name,
                "preparation_status",
                "Entered Trip",
            )
            if doc.trip_status in ("Started", "Paused"):
                frappe.db.set_value(
                    "Shipping Request",
                    row.shipping_request,
                    "request_status",
                    "Out for Delivery",
                )
            elif doc.trip_status == "Completed":
                frappe.db.set_value(
                    "Shipping Request",
                    row.shipping_request,
                    "request_status",
                    "Delivered",
                )
