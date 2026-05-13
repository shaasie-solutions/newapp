import frappe
from frappe import _
from frappe.utils import flt


def get_filters():
    return [
        {
            "fieldname": "truck",
            "label": _("الشاحنة"),
            "fieldtype": "Link",
            "options": "Truck",
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
        {
            "fieldname": "include_inactive",
            "label": _("عرض من ليس لها رحلات في الفترة"),
            "fieldtype": "Check",
            "default": 0,
        },
    ]


def execute(filters=None):
    filters = filters or {}
    columns = [
        {
            "label": _("الشاحنة"),
            "fieldname": "truck",
            "fieldtype": "Link",
            "options": "Truck",
            "width": 160,
        },
        {"label": _("عدد الرحلات"), "fieldname": "trip_count", "fieldtype": "Int", "width": 100},
        {"label": _("عدد الشحنات"), "fieldname": "shipment_count", "fieldtype": "Int", "width": 110},
        {"label": _("إجمالي المصروفات"), "fieldname": "total_expenses", "fieldtype": "Currency", "width": 130},
        {"label": _("إجمالي الإيرادات (متفق)"), "fieldname": "total_revenue", "fieldtype": "Currency", "width": 150},
    ]

    inner_where = ["1=1"]
    vals = []

    if filters.get("from_date"):
        inner_where.append("DATE(COALESCE(ht.departure_date, ht.modified)) >= %s")
        vals.append(filters["from_date"])
    if filters.get("to_date"):
        inner_where.append("DATE(COALESCE(ht.departure_date, ht.modified)) <= %s")
        vals.append(filters["to_date"])
    if filters.get("truck"):
        inner_where.append("ht.truck = %s")
        vals.append(filters["truck"])

    inner_clause = " AND ".join(inner_where)

    outer_parts = []
    if filters.get("truck"):
        outer_parts.append("t.name = %s")
        vals.append(filters["truck"])
    if not filters.get("include_inactive") and not filters.get("truck"):
        outer_parts.append("IFNULL(agg.trip_count, 0) > 0")

    outer_where = ""
    if outer_parts:
        outer_where = " WHERE " + " AND ".join(outer_parts)

    sql = f"""
        SELECT
            t.name AS truck,
            IFNULL(agg.trip_count, 0) AS trip_count,
            IFNULL(agg.shipment_count, 0) AS shipment_count,
            IFNULL(agg.total_expenses, 0) AS total_expenses,
            IFNULL(agg.total_revenue, 0) AS total_revenue
        FROM `tabTruck` t
        LEFT JOIN (
            SELECT
                base.truck AS truck,
                COUNT(*) AS trip_count,
                SUM(base.ship_cnt) AS shipment_count,
                SUM(base.exp_amt) AS total_expenses,
                SUM(base.rev_amt) AS total_revenue
            FROM (
                SELECT
                    ht.truck AS truck,
                    ht.name AS trip,
                    (
                        SELECT COUNT(DISTINCT s.shipping_request)
                        FROM `tabHaulage Trip Shipment` s
                        WHERE s.parent = ht.name
                    ) AS ship_cnt,
                    (
                        SELECT IFNULL(SUM(e.amount), 0)
                        FROM `tabHaulage Trip Expense` e
                        WHERE e.parent = ht.name
                    ) AS exp_amt,
                    (
                        SELECT IFNULL(SUM(IFNULL(sr.agreed_price, 0)), 0)
                        FROM `tabHaulage Trip Shipment` s
                        INNER JOIN `tabShipping Request` sr ON sr.name = s.shipping_request
                        WHERE s.parent = ht.name
                    ) AS rev_amt
                FROM `tabHaulage Trip` ht
                WHERE {inner_clause}
            ) base
            GROUP BY base.truck
        ) agg ON agg.truck = t.name
        {outer_where}
        ORDER BY trip_count DESC, t.name
    """

    data = frappe.db.sql(sql, tuple(vals), as_dict=True)

    for row in data:
        row["total_expenses"] = flt(row.get("total_expenses"))
        row["total_revenue"] = flt(row.get("total_revenue"))

    return columns, data
