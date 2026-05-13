import frappe
from frappe import _
from frappe.utils import flt


def get_filters():
    return [
        {
            "fieldname": "trip",
            "label": _("Trip"),
            "fieldtype": "Link",
            "options": "Haulage Trip",
            "reqd": 0,
        },
        {
            "fieldname": "driver",
            "label": _("Driver"),
            "fieldtype": "Link",
            "options": "Driver",
            "reqd": 0,
        },
        {
            "fieldname": "truck",
            "label": _("Truck"),
            "fieldtype": "Link",
            "options": "Truck",
            "reqd": 0,
        },
        {
            "fieldname": "from_date",
            "label": _("From date"),
            "fieldtype": "Date",
            "reqd": 0,
        },
        {
            "fieldname": "to_date",
            "label": _("To date"),
            "fieldtype": "Date",
            "reqd": 0,
        },
    ]


def execute(filters=None):
    filters = filters or {}
    columns = [
        {
            "label": _("Trip No."),
            "fieldname": "trip",
            "fieldtype": "Link",
            "options": "Haulage Trip",
            "width": 140,
        },
        {"label": _("Status"), "fieldname": "trip_status", "fieldtype": "Data", "width": 100},
        {"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 120},
        {"label": _("Truck"), "fieldname": "truck", "fieldtype": "Link", "options": "Truck", "width": 120},
        {
            "label": _("Route"),
            "fieldname": "shipping_route",
            "fieldtype": "Link",
            "options": "Shipping Route",
            "width": 140,
        },
        {"label": _("Shipment count"), "fieldname": "shipment_count", "fieldtype": "Int", "width": 110},
        {"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 110},
        {"label": _("Expenses"), "fieldname": "expenses", "fieldtype": "Currency", "width": 110},
        {"label": _("Net income"), "fieldname": "net_income", "fieldtype": "Currency", "width": 110},
    ]

    conditions = []
    values = []

    if filters.get("trip"):
        conditions.append("ht.name = %s")
        values.append(filters["trip"])
    if filters.get("driver"):
        conditions.append("ht.driver = %s")
        values.append(filters["driver"])
    if filters.get("truck"):
        conditions.append("ht.truck = %s")
        values.append(filters["truck"])
    if filters.get("from_date"):
        conditions.append("DATE(COALESCE(ht.departure_date, ht.modified)) >= %s")
        values.append(filters["from_date"])
    if filters.get("to_date"):
        conditions.append("DATE(COALESCE(ht.departure_date, ht.modified)) <= %s")
        values.append(filters["to_date"])

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    data = frappe.db.sql(
        f"""
        SELECT
            ht.name AS trip,
            ht.trip_status,
            ht.driver,
            ht.truck,
            ht.shipping_route,
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
        WHERE {where_clause}
        ORDER BY ht.modified DESC
        """,
        tuple(values),
        as_dict=True,
    )

    for row in data:
        row["revenue"] = flt(row.get("revenue"))
        row["expenses"] = flt(row.get("expenses"))
        row["net_income"] = flt(row.get("net_income"))
        row["shipment_count"] = int(row.get("shipment_count") or 0)

    return columns, data
