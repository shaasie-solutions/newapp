# haulage_mgmt — haulage logistics for ERPNext

A **Frappe** app on **ERPNext** for truck shipping: fleet, drivers, routes, trips, expenses, Sales Invoices, and draft Journal Entries for trip costs.

**Version:** see `haulage_mgmt/__init__.py` and Git tags (e.g. `v0.1.1`).

---

## Language (English UI + Arabic)

- **Source strings** in the app are **English** (Python `_("…")`, client `__(…)`, DocType labels, workspace, print format).
- **Arabic** is supplied via the official Frappe pattern: CSV at **`translations/ar.csv`** in the app root (next to `setup.py`). See the [Frappe translations guide](https://docs.frappe.io/framework/user/en/guides/basics/translations).
- After changing `ar.csv` or adding client strings, run **`bench --site <yoursite> clear-cache`**. If you change client-translated strings, also run **`bench build --app haulage_mgmt`**.
- Users see Arabic when their **Desk language** is set to Arabic (and translations are loaded).

---

## Requirements

- [Frappe Bench](https://docs.frappe.io/framework/user/en/installation) with a site that has **ERPNext** installed
- Python 3.10+ (match your bench environment)

---

## Install

This Git repository is a **monorepo**: the Frappe app (with `setup.py`) lives in the **`haulage_mgmt/`** subfolder, not at the repository root. Point `bench get-app` at that folder.

```bash
cd /path/to/frappe-bench
# From a clone of this repo (adjust the path to your clone):
bench get-app /path/to/newapp/haulage_mgmt haulage_mgmt
# or after copying only the app folder into apps/:
bench get-app ./apps/haulage_mgmt

bench --site yoursite.com install-app haulage_mgmt
bench --site yoursite.com migrate
bench build --app haulage_mgmt
```

`install-app` runs migrations for the app; run **`bench migrate`** again after pulling updates. The app declares **`required_apps = ["erpnext"]`** — install **ERPNext** on the site first.

---

## Uninstall and removal

**From a site (drops app DocTypes and module data for that site):**

```bash
# Optional: list what would be removed
bench --site yoursite.com uninstall-app haulage_mgmt --dry-run

bench --site yoursite.com uninstall-app haulage_mgmt --yes --no-backup
```

`before_uninstall` removes the **Fleet Manager** role and its **Has Role** rows so they do not remain orphaned. Standard ERPNext documents you created while using the app (e.g. Sales Invoices, Journal Entries) are **not** deleted.

**Remove the app code from the bench** (after it is uninstalled on every site that had it, or use `--force` if bench insists):

```bash
bench remove-app haulage_mgmt --force
```

Then you can delete the app directory from `apps/` if anything remains, or remove your git clone.

---

## Initial setup

1. **Haulage Logistics Settings**
   - **Default freight Item (Sales Invoice):** an `Item` (typically a service) used on the Sales Invoice line when you use **Create Sales Invoice for shipment**.
   - **Trip expense credit account (Journal Entry):** a Chart of Accounts account that is **not** of root type Expense (e.g. cash or a clearing account) for the credit side of the trip expense JE.

2. **Roles**
   - **Fleet Manager** is created on `migrate`. Assign it on **User** as needed.
   - For **Create expense journal (draft)**, users need permission to create **Journal Entry** (often via **Role Permission Manager**).

3. **Scheduler**
   - A daily job creates **ToDo** reminders for expiring truck/driver documents. Ensure `bench schedule` (or your hosting equivalent) is running.

---

## Suggested workflow

1. Master data: trucks, drivers, shipping routes, haulage expense types (each linked to an expense **Account**).
2. **Customer** in ERPNext for clients.
3. **Shipping Request**
4. **Shipment Preparation** until the cargo is **Ready for Trip**.
5. **Haulage Trip** with shipments, truck, driver, and company.
6. Trip events, expenses, Sales Invoice, and expense Journal Entry as needed.
7. Reports under **Haulage Logistics** or the **Fleet Haulage** workspace.

---

## Main components

| DocType / feature | Description |
|-------------------|-------------|
| Truck, Driver | Fleet master data |
| Shipping Route | Routes |
| Haulage Expense Type | Expense categories + **Account** link |
| Shipping Request | Customer shipping request |
| Shipment Preparation | Pre-trip cargo preparation |
| Haulage Trip | Operational trip with shipments, events, expenses |
| Script reports | Trip Financial Summary, Driver Performance, Truck Performance |
| Workspace | Fleet Haulage desk shortcuts |
| Customer dashboard | Shipping requests from **Customer** |
| Print format | Haulage Trip Dispatch |

---

## Whitelisted API

- `haulage_mgmt.haulage_logistics.api.create_sales_invoice_from_shipment`
- `haulage_mgmt.haulage_logistics.api.create_trip_expense_journal_entry`

Used by buttons on **Haulage Trip**.

---

## License

See `license.txt` (MIT unless stated otherwise).

---

## Official references

- [Frappe Framework](https://docs.frappe.io/framework)
- [ERPNext](https://docs.frappe.io/erpnext)
- [Custom apps](https://docs.frappe.io/erpnext/user/manual/en/customize-erpnext)
- [Translations](https://docs.frappe.io/framework/user/en/guides/basics/translations)
