from frappe import _


def get_dashboard_data(data=None, **kwargs):
    """يضيف طلبات الشحن إلى لوحة تحكم العميل في ERPNext."""
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return data
    transactions = data.setdefault("transactions", [])
    transactions.append({"label": _("الشحن والأسطول"), "items": ["Shipping Request"]})
    return data
