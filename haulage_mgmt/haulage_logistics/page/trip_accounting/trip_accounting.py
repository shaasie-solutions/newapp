import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_trip_accounting_list(status=None):
    """Trips with revenue, expenses, and net income for the Trip Accounting desk page."""
    conditions = ["1=1"]
    values = []
    if status:
        conditions.append("ht.trip_status = %s")
        values.append(status)

    where = " AND ".join(conditions)
    rows = frappe.db.sql(
        f"""
        SELECT
            ht.name AS trip,
            ht.trip_status,
            ht.driver,
            ht.truck,
            DATE(COALESCE(ht.departure_date, ht.modified)) AS trip_date,
            (
                SELECT COUNT(DISTINCT s.shipping_request)
                FROM `tabHaulage Trip Shipment` s
                WHERE s.parent = ht.name
            ) AS shipment_count,
            IFNULL(rev.revenue, 0) AS revenue,
            IFNULL(exp.expenses, 0) AS expenses,
            IFNULL(rev.revenue, 0) - IFNULL(exp.expenses, 0) AS net_income
        FROM `tabHaulage Trip` ht
        LEFT JOIN (
            SELECT parent, SUM(amount) AS expenses
            FROM `tabHaulage Trip Expense`
            GROUP BY parent
        ) exp ON exp.parent = ht.name
        LEFT JOIN (
            SELECT s.parent, SUM(IFNULL(sr.agreed_price, 0)) AS revenue
            FROM `tabHaulage Trip Shipment` s
            INNER JOIN `tabShipping Request` sr ON sr.name = s.shipping_request
            GROUP BY s.parent
        ) rev ON rev.parent = ht.name
        WHERE {where}
        ORDER BY COALESCE(ht.departure_date, ht.modified) DESC, ht.name DESC
        LIMIT 500
        """,
        tuple(values),
        as_dict=True,
    )
    for row in rows:
        row["revenue"] = flt(row.get("revenue"))
        row["expenses"] = flt(row.get("expenses"))
        row["net_income"] = flt(row.get("net_income"))
        row["shipment_count"] = int(row.get("shipment_count") or 0)
    return rows


@frappe.whitelist()
def get_trip_accounting_detail(trip_name):
    """Revenue lines and expense totals for the trip accounting form view."""
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
    return {
        "trip": trip_name,
        "trip_status": trip.trip_status,
        "revenue_lines": revenue_lines,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": total_revenue - total_expenses,
        "trip_journal_entry": trip.trip_journal_entry,
    }
