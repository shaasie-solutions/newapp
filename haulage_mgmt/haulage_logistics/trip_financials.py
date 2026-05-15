"""Shared trip revenue, expenses, and custody totals (list, form, print)."""

import frappe
from frappe.utils import flt


def get_trip_financial_summary(trip_name):
    """Financial breakdown for one trip (used by accounting UI and print)."""
    trip_name = (trip_name or "").strip()
    if not trip_name or not frappe.db.exists("Haulage Trip", trip_name):
        return {
            "revenue_lines": [],
            "total_revenue": 0.0,
            "total_expenses": 0.0,
            "total_custody": 0.0,
            "net_income": 0.0,
            "trip_status": "",
        }

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
    }
