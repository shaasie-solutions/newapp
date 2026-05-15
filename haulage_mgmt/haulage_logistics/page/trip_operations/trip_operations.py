import frappe
from frappe.utils import getdate


@frappe.whitelist()
def get_trip_operations_list(status=None):
    """All trips with status for the operations list page."""
    filters = {}
    if status:
        filters["trip_status"] = status

    rows = frappe.get_all(
        "Haulage Trip",
        filters=filters,
        fields=["name", "trip_status", "truck", "driver", "departure_date", "modified"],
        order_by="modified desc",
        limit_page_length=500,
    )
    for row in rows:
        row["trip"] = row.name
        dt = row.departure_date or row.modified
        row["trip_date"] = getdate(dt) if dt else None
    return rows
