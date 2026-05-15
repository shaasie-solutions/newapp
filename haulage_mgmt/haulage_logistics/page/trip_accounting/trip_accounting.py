import frappe

from haulage_mgmt.haulage_logistics.report.report_utils import (
    normalize_money_rows,
    trip_metrics_subquery,
)
from haulage_mgmt.haulage_logistics.trip_financials import get_trip_financial_summary


@frappe.whitelist()
def get_trip_accounting_list(status=None):
    """Trips with revenue, expenses, custody, and net income for the operations hub."""
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
    """Revenue lines and financial totals for the trip accounting form."""
    return get_trip_financial_summary(trip_name)
