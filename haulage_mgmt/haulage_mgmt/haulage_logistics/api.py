from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def create_sales_invoice_from_shipment(trip_name, shipping_request_name):
    trip_name = (trip_name or "").strip()
    shipping_request_name = (shipping_request_name or "").strip()
    if not frappe.has_permission("Haulage Trip", "write", doc=trip_name):
        frappe.throw(_("ليس لديك صلاحية تعديل هذه الرحلة."), frappe.PermissionError)
    if not frappe.has_permission("Sales Invoice", "create"):
        frappe.throw(_("ليس لديك صلاحية إنشاء فاتورة بيع."), frappe.PermissionError)

    trip = _validate_shipment_on_trip(trip_name, shipping_request_name)

    item_code = frappe.db.get_single_value(
        "Haulage Logistics Settings", "default_freight_item"
    )
    if not item_code:
        frappe.throw(
            _(
                "يرجى فتح «إعدادات لوجستيات الشحن» وتحديد صنف خدمة الشحن الافتراضي قبل إنشاء الفاتورة."
            )
        )

    sr = frappe.get_doc("Shipping Request", shipping_request_name)
    if not frappe.has_permission("Shipping Request", "read", doc=sr.name):
        frappe.throw(_("ليس لديك صلاحية قراءة طلب الشحن."), frappe.PermissionError)

    company = trip.get("company") or frappe.defaults.get_user_default("Company")
    if not company:
        company = frappe.db.get_value("Company", {}, "name")

    si = frappe.new_doc("Sales Invoice")
    si.customer = sr.customer
    si.company = company
    si.posting_date = frappe.utils.today()
    si.due_date = frappe.utils.add_days(si.posting_date, 30)
    si.append(
        "items",
        {
            "item_code": item_code,
            "qty": 1,
            "rate": flt(sr.agreed_price),
            "description": _("شحن — طلب {0} — رحلة {1}").format(sr.name, trip_name),
        },
    )
    if hasattr(si, "set_missing_values"):
        si.set_missing_values()
    si.flags.ignore_permissions = True
    si.insert()
    return {"name": si.name}


@frappe.whitelist()
def create_trip_expense_journal_entry(trip_name):
    """يُنشئ قيد يومية (مسودة) لمجموع مصروفات الرحلة: مدين حسابات المصروف، دائن حساب الإعدادات."""
    trip_name = (trip_name or "").strip()
    if not frappe.has_permission("Haulage Trip", "write", doc=trip_name):
        frappe.throw(_("ليس لديك صلاحية تعديل هذه الرحلة."), frappe.PermissionError)
    if not frappe.has_permission("Journal Entry", "create"):
        frappe.throw(
            _("يلزم صلاحية «إنشاء قيد يومية» (مثلاً مدير حسابات أو صلاحية مخصّصة على Journal Entry)."),
            frappe.PermissionError,
        )

    trip = frappe.get_doc("Haulage Trip", trip_name)
    if trip.trip_status == "Cancelled":
        frappe.throw(_("لا يمكن ترحيل قيد لرحلة ملغاة."))
    if trip.trip_journal_entry:
        frappe.throw(_("يوجد قيد يومية مرتبط بالفعل: {0}").format(trip.trip_journal_entry))

    credit_acc = frappe.db.get_single_value(
        "Haulage Logistics Settings", "trip_expense_credit_account"
    )
    if not credit_acc:
        frappe.throw(
            _("حدّد في «إعدادات لوجستيات الشحن» الحساب الدائن لترحيل مصروفات الرحلة.")
        )

    _validate_account_company(credit_acc, trip.company)

    totals = defaultdict(float)
    for row in trip.get("trip_expenses") or []:
        if not row.expense_type or not flt(row.amount):
            continue
        exp_acc = frappe.db.get_value("Haulage Expense Type", row.expense_type, "account")
        if not exp_acc:
            frappe.throw(_("نوع المصروف {0} بدون حساب محاسبي.").format(row.expense_type))
        _validate_account_company(exp_acc, trip.company)
        totals[exp_acc] += flt(row.amount)

    if not totals:
        frappe.throw(_("لا توجد بنود مصروفات بمبالغ لترحيلها."))

    je = frappe.new_doc("Journal Entry")
    je.company = trip.company
    je.posting_date = frappe.utils.today()
    je.voucher_type = "Journal Entry"
    je.user_remark = _("مصروفات رحلة شحن {0}").format(trip.name)

    grand = 0.0
    for acc, amt in totals.items():
        je.append(
            "accounts",
            {
                "account": acc,
                "debit_in_account_currency": amt,
                "credit_in_account_currency": 0,
            },
        )
        grand += amt

    je.append(
        "accounts",
        {
            "account": credit_acc,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": grand,
        },
    )

    je.flags.ignore_permissions = True
    je.insert()
    frappe.db.set_value("Haulage Trip", trip.name, "trip_journal_entry", je.name)
    return {"name": je.name}


def _validate_account_company(account, company):
    acc_co = frappe.db.get_value("Account", account, "company")
    if acc_co and company and acc_co != company:
        frappe.throw(_("الحساب {0} لا يتبع الشركة {1}.").format(account, company))


def _validate_shipment_on_trip(trip_name, shipping_request_name):
    trip = frappe.get_doc("Haulage Trip", trip_name)
    linked = {r.shipping_request for r in (trip.get("shipments") or []) if r.shipping_request}
    if shipping_request_name not in linked:
        frappe.throw(_("طلب الشحن المحدد غير مرتبط بهذه الرحلة."))
    return trip
