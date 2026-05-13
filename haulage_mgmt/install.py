import frappe


def _first_company_name():
    rows = frappe.get_all("Company", pluck="name", order_by="creation asc", limit=1)
    return rows[0] if rows else None


def before_migrate():
    """Create Fleet Manager role before DocType sync so JSON permissions import cleanly."""
    if frappe.db.exists("Role", "Fleet Manager"):
        return
    doc = frappe.new_doc("Role")
    doc.role_name = "Fleet Manager"
    doc.desk_access = 1
    doc.insert(ignore_permissions=True)


def after_migrate():
    """Backfill Company on legacy Haulage Trip rows when a default company exists."""
    if not frappe.db.exists("DocType", "Haulage Trip"):
        return
    company = _first_company_name()
    if not company:
        return
    frappe.db.sql(
        """
        UPDATE `tabHaulage Trip`
        SET company = %s
        WHERE IFNULL(company, '') = ''
        """,
        (company,),
    )
    _fix_workspace_sidebar()


def _fix_workspace_sidebar():
    """Keep workspace title in sync with name (desk routes slug the name) and detach from any parent."""
    ws = "Haulage Logistics"
    if not frappe.db.exists("Workspace", ws):
        return
    row = frappe.db.get_value("Workspace", ws, ["title", "parent_page"], as_dict=True)
    if not row:
        return
    updates = {}
    if row.get("title") != ws:
        updates["title"] = ws
    if row.get("parent_page"):
        updates["parent_page"] = ""
    if updates:
        frappe.db.set_value("Workspace", ws, updates)


def before_uninstall():
    """Remove roles created by this app so they do not linger after uninstall."""
    role = "Fleet Manager"
    if not frappe.db.exists("Role", role):
        return
    frappe.db.sql("DELETE FROM `tabHas Role` WHERE role=%s", (role,))
    try:
        frappe.delete_doc("Role", role, force=True, ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "haulage_mgmt before_uninstall: Role Fleet Manager")
