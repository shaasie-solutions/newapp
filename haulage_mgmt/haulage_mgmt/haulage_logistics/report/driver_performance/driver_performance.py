import frappe
from frappe import _
from frappe.utils import flt


def get_filters():
    return [
        {
            "fieldname": "driver",
            "label": _("Driver"),
            "fieldtype": "Link",
            "options": "Driver",
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
        {
            "fieldname": "include_inactive",
            "label": _("Include records with no trips in period"),
            "fieldtype": "Check",
            "default": 0,
        },
    ]


def execute(filters=None):
    filters = filters or {}
    columns = [
        {
            "label": _("Driver"),
            "fieldname": "driver",
            "fieldtype": "Link",
            "options": "Driver",
            "width": 160,
        },
        {"label": _("Trip count"), "fieldname": "trip_count", "fieldtype": "Int", "width": 100},
        {"label": _("Shipment count"), "fieldname": "shipment_count", "fieldtype": "Int", "width": 110},
        {"label": _("Total expenses"), "fieldname": "total_expenses", "fieldtype": "Currency", "width": 130},
        {"label": _("Total agreed revenue"), "fieldname": "total_revenue", "fieldtype": "Currency", "width": 150},
    ]

    inner_where = ["1=1"]
    vals = []

    if filters.get("from_date"):
        inner_where.append("DATE(COALESCE(ht.departure_date, ht.modified)) >= %s")
        vals.append(filters["from_date"])
    if filters.get("to_date"):
        inner_where.append("DATE(COALESCE(ht.departure_date, ht.modified)) <= %s")
        vals.append(filters["to_date"])
    if filters.get("driver"):
        inner_where.append("ht.driver = %s")
        vals.append(filters["driver"])

    inner_clause = " AND ".join(inner_where)

    outer_parts = []
    if filters.get("driver"):
        outer_parts.append("d.name = %s")
        vals.append(filters["driver"])
    if not filters.get("include_inactive") and not filters.get("driver"):
        outer_parts.append("IFNULL(agg.trip_count, 0) > 0")

    outer_where = ""
    if outer_parts:
        outer_where = " WHERE " + " AND ".join(outer_parts)

    sql = f"""
        SELECT
            d.name AS driver,
            IFNULL(agg.trip_count, 0) AS trip_count,
            IFNULL(agg.shipment_count, 0) AS shipment_count,
            IFNULL(agg.total_expenses, 0) AS total_expenses,
            IFNULL(agg.total_revenue, 0) AS total_revenue
        FROM `tabDriver` d
        LEFT JOIN (
            SELECT
                base.driver AS driver,
                COUNT(*) AS trip_count,
                SUM(base.ship_cnt) AS shipment_count,
                SUM(base.exp_amt) AS total_expenses,
                SUM(base.rev_amt) AS total_revenue
            FROM (
                SELECT
                    ht.driver AS driver,
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
            GROUP BY base.driver
        ) agg ON agg.driver = d.name
        {outer_where}
        ORDER BY trip_count DESC, d.name
    """

    data = frappe.db.sql(sql, tuple(vals), as_dict=True)

    for row in data:
        row["total_expenses"] = flt(row.get("total_expenses"))
        row["total_revenue"] = flt(row.get("total_revenue"))

    return columns, data
