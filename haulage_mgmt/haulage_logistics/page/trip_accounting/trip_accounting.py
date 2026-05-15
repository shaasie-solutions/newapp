import frappe
from frappe import _
from frappe.utils import flt

from haulage_mgmt.haulage_logistics.report.report_utils import (
    normalize_money_rows,
    trip_metrics_subquery,
)


@frappe.whitelist()
def get_trip_accounting_list(status=None):
    """Trips with revenue, expenses, custody, and net income for the list page."""
    conditions = ["1=1"]
    values = []
    if status:
        conditions.append("ht.trip_status = %s")
        values.append(status)

    where = " AND ".join(conditions)
    rows = frappe.db.sql(
        f"""
        SELECT *
        FROM ({trip_metrics_subquery(where)}) AS fin
        ORDER BY fin.trip_date DESC, fin.trip DESC
        LIMIT 500
        """,
        tuple(values),
        as_dict=True,
    )
    normalize_money_rows(rows)
    return rows


@frappe.whitelist()
def get_trip_accounting_detail(trip_name):
    """Revenue lines and financial totals for the trip accounting entry page."""
    trip_name = (trip_name or "").strip()
    if not trip_name or not frappe.db.exists("Haulage Trip", trip_name):
        frappe.throw(_("Trip {0} does not exist.").format(trip_name))

    trip = frappe.get_doc("Haulage Trip", trip_name)
    revenue_lines = []
    total_revenue = 0.0
    for row in trip.get("shipments") or []:
        if not row.shipping_request:
            continue
        sr = frappe.db.get_value(
            "Shipping Request",
            row.shipping_request,
            ["customer", "agreed_price", "pickup_location", "delivery_location"],
            as_dict=True,
        )
        if not sr:
            continue
        amount = flt(sr.agreed_price)
        total_revenue += amount
        revenue_lines.append(
            {
                "shipping_request": row.shipping_request,
                "customer": sr.customer,
                "pickup_location": sr.pickup_location or "",
                "delivery_location": sr.delivery_location or "",
                "agreed_price": amount,
            }
        )

    total_expenses = sum(flt(e.amount) for e in (trip.get("trip_expenses") or []))
    total_custody = sum(flt(c.amount) for c in (trip.get("trip_custodies") or []))
    return {
        "trip": trip_name,
        "trip_status": trip.trip_status,
        "driver": trip.driver,
        "truck": trip.truck,
        "revenue_lines": revenue_lines,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "total_custody": total_custody,
        "net_income": total_revenue - total_expenses - total_custody,
        "trip_journal_entry": trip.trip_journal_entry,
    }
