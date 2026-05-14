import json
from pathlib import Path

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
    """Purge replaced desk artifacts; sync workspace from app JSON; backfill Company on legacy trips."""
    _migrate_truck_busy_to_reserved()
    _purge_legacy_haulage_reports()
    _sync_haulage_workspace_from_json()
    _fix_workspace_sidebar()
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


def _migrate_truck_busy_to_reserved():
    """Rename legacy truck status Busy -> Reserved for Trip on existing rows."""
    if not frappe.db.exists("DocType", "Truck"):
        return
    frappe.db.sql(
        "UPDATE `tabTruck` SET truck_status = %s WHERE truck_status = %s",
        ("Reserved for Trip", "Busy"),
    )


def _purge_legacy_haulage_reports():
    """Remove script reports superseded by Haulage Operations Summary (keeps desk links valid)."""
    if not frappe.db.exists("DocType", "Report"):
        return
    for report in ("Trip Financial Summary", "Driver Performance", "Truck Performance"):
        if not frappe.db.exists("Report", report):
            continue
        try:
            frappe.delete_doc("Report", report, force=True, ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"haulage_mgmt: purge legacy report {report}")


def _sync_haulage_workspace_from_json():
    """Replace workspace content, shortcuts, and links from the app bundle.

    Avoids duplicate or stale shortcut rows on sites that imported an older workspace.
    """
    try:
        _do_sync_haulage_workspace_from_json()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "haulage_mgmt: workspace sync failed")


def _do_sync_haulage_workspace_from_json():
    ws_name = "Haulage Logistics"
    if not frappe.db.exists("Workspace", ws_name):
        return
    path = Path(frappe.get_app_path("haulage_mgmt")) / "haulage_logistics" / "workspace" / "haulage_logistics" / "haulage_logistics.json"
    if not path.exists():
        return
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    doc = frappe.get_doc("Workspace", ws_name)
    doc.content = data.get("content") or "[]"
    doc.title = data.get("title") or ws_name
    doc.label = data.get("label") or ws_name
    for row in list(doc.shortcuts):
        doc.remove(row)
    for row in list(doc.links):
        doc.remove(row)
    for row in data.get("shortcuts") or []:
        doc.append("shortcuts", row)
    for row in data.get("links") or []:
        doc.append("links", row)
    doc.parent_page = ""
    doc.save(ignore_permissions=True)


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
