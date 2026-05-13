import frappe


def before_migrate():
    """يُنشئ دور Fleet Manager قبل مزامنة أنواع المستندات حتى تُستورد صلاحياته من JSON."""
    if frappe.db.exists("Role", "Fleet Manager"):
        return
    doc = frappe.new_doc("Role")
    doc.role_name = "Fleet Manager"
    doc.desk_access = 1
    doc.insert(ignore_permissions=True)


def after_migrate():
    """بيانات قديمة: تعبئة حقل الشركة في الرحلات إن وُجدت شركة افتراضية."""
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
