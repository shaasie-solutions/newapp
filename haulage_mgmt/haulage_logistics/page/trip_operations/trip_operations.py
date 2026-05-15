"""Desk page API: trip operations list and trip accounting list (single hub)."""

import frappe
from frappe import _
from frappe.utils import getdate

from haulage_mgmt.haulage_logistics.report.report_utils import (
    normalize_money_rows,
    trip_metrics_subquery,
)
from haulage_mgmt.haulage_logistics.trip_financials import get_trip_financial_summary


@frappe.whitelist()
def get_trip_operations_list(status=None):
    """Operational list: trip, status, driver, truck, date."""
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


@frappe.whitelist()
def get_trip_accounting_list(status=None):
    """Accounting list: revenue, expenses, custody, net income per trip."""
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
    """Financial breakdown for accounting form and print summary."""
    trip_name = (trip_name or "").strip()
    if trip_name and not frappe.has_permission("Haulage Trip", "read", doc=trip_name):
        frappe.throw(_("You do not have permission to read this trip."), frappe.PermissionError)
    return get_trip_financial_summary(trip_name)
