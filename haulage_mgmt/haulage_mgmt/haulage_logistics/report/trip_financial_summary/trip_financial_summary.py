import frappe
from frappe import _
from frappe.utils import flt


def get_filters():
    return [
        {
            "fieldname": "trip",
            "label": _("الرحلة"),
            "fieldtype": "Link",
            "options": "Haulage Trip",
            "reqd": 0,
        },
        {
            "fieldname": "from_date",
            "label": _("من تاريخ"),
            "fieldtype": "Date",
            "reqd": 0,
        },
        {
            "fieldname": "to_date",
            "label": _("إلى تاريخ"),
            "fieldtype": "Date",
            "reqd": 0,
        },
    ]


def execute(filters=None):
    filters = filters or {}
    columns = [
        {
            "label": _("رقم الرحلة"),
            "fieldname": "trip",
            "fieldtype": "Link",
            "options": "Haulage Trip",
            "width": 140,
        },
        {"label": _("الحالة"), "fieldname": "trip_status", "fieldtype": "Data", "width": 100},
        {"label": _("السائق"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 120},
        {"label": _("الشاحنة"), "fieldname": "truck", "fieldtype": "Link", "options": "Truck", "width": 120},
        {
            "label": _("المسار"),
            "fieldname": "shipping_route",
            "fieldtype": "Link",
            "options": "Shipping Route",
            "width": 140,
        },
        {"label": _("الإيرادات"), "fieldname": "revenue", "fieldtype": "Currency", "width": 110},
        {"label": _("المصروفات"), "fieldname": "expenses", "fieldtype": "Currency", "width": 110},
        {"label": _("صافي الدخل"), "fieldname": "net_income", "fieldtype": "Currency", "width": 110},
    ]

    conditions = []
    values = []

    if filters.get("trip"):
        conditions.append("ht.name = %s")
        values.append(filters["trip"])
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

    return columns, data
