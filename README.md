# newapp — haulage_mgmt (Frappe / ERPNext)

Git repository for the **`haulage_mgmt`** custom app: fleet haulage, shipping requests, trips, expenses, and ERPNext billing (Sales Invoice / Journal Entry).

**Version:** see `haulage_mgmt/__init__.py` and Git tags (e.g. `v0.1.3`).

---

## Install with Bench (Git URL + tag/branch)

`setup.py` is at the **repository root**, so `bench get-app` works with the GitHub URL and `--branch`:

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/shaasie-solutions/newapp.git --branch v0.1.3

bench --site yoursite.com install-app haulage_mgmt
bench --site yoursite.com migrate
bench build --app haulage_mgmt
bench --site yoursite.com clear-cache
```

The **Haulage Management** app tile opens workspace **`/desk/haulage-logistics`** (slug of **Haulage Logistics**). Some setups also accept **`/app/haulage-logistics`** depending on Frappe version.

Bench clones the repo into `apps/newapp` (from the repo name). The Python package name and **`bench install-app`** target remain **`haulage_mgmt`** (from `setup.py`).

The app requires **ERPNext** (`required_apps = ["erpnext"]`) on the site.

---

## Repository layout

| Path | Description |
|------|-------------|
| `setup.py`, `requirements.txt`, `MANIFEST.in`, `license.txt` | Frappe app root (Bench expects `setup.py` here). |
| `haulage_mgmt/` | Python package (`hooks.py`, modules, DocTypes). |
| `translations/ar.csv` | Arabic translations. |
| `CHANGELOG.md` | Release notes. |

---

## Documentation

Full workflow, uninstall, i18n, and setup details are in the sections below (same content as the former app-level README).

---

## Language (English UI + Arabic)

- **Source strings** are **English** (Python `_("…")`, client `__(…)`).
- **Arabic** via **`translations/ar.csv`** next to `setup.py`. See the [Frappe translations guide](https://docs.frappe.io/framework/user/en/guides/basics/translations).
- After changing `ar.csv` or client strings: **`bench --site <site> clear-cache`** and **`bench build --app haulage_mgmt`** when needed.

---

## Requirements

- [Frappe Bench](https://docs.frappe.io/framework/user/en/installation) with **ERPNext** installed on the site.
- Python 3.10+ (match your bench).

---

## Uninstall and removal

```bash
bench --site yoursite.com uninstall-app haulage_mgmt --dry-run
bench --site yoursite.com uninstall-app haulage_mgmt --yes --no-backup
bench remove-app haulage_mgmt --force
```

`before_uninstall` removes the **Fleet Manager** role and related **Has Role** rows. Standard ERPNext documents (e.g. Sales Invoices) are **not** deleted.

---

## Initial setup

1. **Haulage Logistics Settings** — default freight **Item**; trip expense **credit** account (not an Expense root type).
2. **Fleet Manager** role (created on migrate); assign on **User**. Journal Entry permission for expense posting.
3. **`bench schedule`** for daily fleet document **ToDo** reminders.

---

## Suggested workflow

1. Master data: trucks, drivers, routes, haulage expense types (with **Account**).
2. **Customer** → **Shipping Request** → **Shipment Preparation** → **Haulage Trip** (shipments, events, expenses).
3. Reports and **Haulage Logistics** workspace (also under the **Haulage Management** app icon when `add_to_apps_screen` is active).

---

## Whitelisted API

- `haulage_mgmt.haulage_logistics.api.create_sales_invoice_from_shipment`
- `haulage_mgmt.haulage_logistics.api.create_trip_expense_journal_entry`

---

## License

See `license.txt` (MIT unless stated otherwise).

---

## Official references

- [Frappe Framework](https://docs.frappe.io/framework)
- [ERPNext](https://docs.frappe.io/erpnext)
- [Translations](https://docs.frappe.io/framework/user/en/guides/basics/translations)
