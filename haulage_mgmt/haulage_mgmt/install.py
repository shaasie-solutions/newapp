import frappe


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
    company = frappe.db.get_value("Company", {}, "name")
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
