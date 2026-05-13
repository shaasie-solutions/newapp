import frappe
from frappe import _
from frappe.utils import add_days, getdate, today


def send_fleet_expiry_reminders():
    """تذكير يومي عبر مهمة: وثائق شاحنات وسائقين تنتهي خلال 30 يوماً."""
    horizon = add_days(today(), 30)
    trucks = frappe.get_all(
        "Truck",
        filters={"truck_status": ("!=", "Stopped")},
        or_filters=[
            ["license_end_date", "<=", horizon],
            ["insurance_end_date", "<=", horizon],
        ],
        fields=["name", "license_plate", "license_end_date", "insurance_end_date"],
        limit=200,
    )
    drivers = frappe.get_all(
        "Driver",
        filters={"driver_status": ("=", "Active")},
        or_filters=[["license_expiry", "<=", horizon]],
        fields=["name", "full_name", "license_expiry"],
        limit=200,
    )
    if not trucks and not drivers:
        return

    lines = []
    for t in trucks:
        if t.license_end_date and getdate(t.license_end_date) <= getdate(horizon):
            lines.append(
                _("شاحنة {0}: انتهاء الترخيص {1}").format(t.license_plate or t.name, t.license_end_date)
            )
        if t.insurance_end_date and getdate(t.insurance_end_date) <= getdate(horizon):
            lines.append(
                _("شاحنة {0}: انتهاء التأمين {1}").format(t.license_plate or t.name, t.insurance_end_date)
            )
    for d in drivers:
        if d.license_expiry and getdate(d.license_expiry) <= getdate(horizon):
            lines.append(
                _("سائق {0}: انتهاء الرخصة {1}").format(d.full_name or d.name, d.license_expiry)
            )

    if not lines:
        return

    body = "\n".join(lines[:50])
    prefix = f"[Haulage {today()}] "
    users = frappe.get_all(
        "Has Role",
        filters={"role": ("in", ["Fleet Manager", "System Manager"]), "parenttype": "User"},
        pluck="parent",
        distinct=True,
    )
    for user in users:
        if user in ("Guest", "Administrator"):
            continue
        if frappe.db.exists(
            "ToDo",
            {"allocated_to": user, "description": ("like", f"{prefix}%")},
        ):
            continue
        try:
            td = frappe.new_doc("ToDo")
            td.description = prefix + _("وثائق تنتهي قريباً:\n") + body
            td.allocated_to = user
            td.status = "Open"
            td.priority = "Medium"
            td.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "haulage_mgmt fleet reminder")
