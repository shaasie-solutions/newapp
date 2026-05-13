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
            frappe.throw(_("حدد الشركة في الرحلة (لا توجد شركة افتراضية للمستخدم)."))
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
            frappe.throw(_("أضف شحنة واحدة على الأقل للرحلة (ما لم تكن الرحلة ملغاة)."))
        seen = set()
        for row in self.get("shipments") or []:
            if not row.shipping_request:
                continue
            if row.shipping_request in seen:
                frappe.throw(_("طلب الشحن {0} مكرر في جدول الشحنات.").format(row.shipping_request))
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
                    _("يجب إنشاء سجل تجهيز الشحنة لطلب {0} قبل إضافته للرحلة.").format(
                        row.shipping_request
                    )
                )
            if prep.preparation_status != "Ready for Trip":
                frappe.throw(
                    _("طلب {0} ليس بحالة «جاهز للدخول في رحلة» في التجهيز.").format(
                        row.shipping_request
                    )
                )
            if not prep.cargo_prepared:
                frappe.throw(_("يجب تأكيد تجهيز البضائع لطلب {0}.").format(row.shipping_request))
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
                    _("تحذير: طلب {0} مسجّل على مسار {1} يختلف عن مسار الرحلة.").format(
                        row.shipping_request, sr_route
                    ),
                    indicator="orange",
                    title=_("اختلاف مسار"),
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
                        _("طلب الشحن {0} مرتبط بالفعل بالرحلة النشطة {1}.").format(
                            row.shipping_request, parent
                        )
                    )

    def _validate_truck_and_driver(self):
        if self.trip_status in ("Cancelled", "Completed"):
            return
        if self.driver:
            st = frappe.db.get_value("Driver", self.driver, "driver_status")
            if st and st != "Active" and self.trip_status in ("Started", "Paused", "Preparing"):
                frappe.throw(_("السائق {0} ليس بحالة «نشط».").format(self.driver))
        if self.truck:
            st = frappe.db.get_value("Truck", self.truck, "truck_status")
            if st == "Stopped" and self.trip_status != "Cancelled":
                frappe.throw(_("الشاحنة {0} متوقفة ولا يمكن استخدامها في الرحلات.").format(self.truck))
            if st == "Maintenance" and self.trip_status in ("Started", "Paused"):
                frappe.throw(_("الشاحنة {0} تحت الصيانة.").format(self.truck))

    def _validate_trip_status_consistency(self):
        if self.trip_status != "Completed":
            return
        events = [e.event_type for e in (self.get("trip_events") or []) if e.event_type]
        if events and events[-1] != "Return":
            frappe.msgprint(
                _(
                    "تم ضبط حالة الرحلة «منتهية» دون أن يكون آخر حدث «رجوع». "
                    "يُفضّل تسجيل حدث «رجوع» لإغلاق الرحلة بدقة."
                ),
                indicator="orange",
                title=_("تنبيه أحداث الرحلة"),
            )


def refresh_truck_fleet_status(truck_name):
    """يحدّث حالة الشاحنة إلى مشغولة إن وُجدت رحلة نشطة، وإلا متاحة (مع احترام الصيانة/التوقف)."""
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
