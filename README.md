# newapp — haulage_mgmt (Frappe / ERPNext)

Git repository for the **`haulage_mgmt`** custom app: fleet haulage, shipping requests, trips, trip accounting (expenses and custody), and ERPNext billing.

**Version:** see `haulage_mgmt/__init__.py` and Git tags (e.g. `v0.1.18`).

---

## Install with Bench (Git URL + tag/branch)

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/shaasie-solutions/newapp.git --branch v0.1.18

bench --site yoursite.com install-app haulage_mgmt
bench --site yoursite.com migrate
bench build --app haulage_mgmt
bench --site yoursite.com clear-cache
```

Desk workspace: **`/desk/haulage-logistics`** (app tile **Haulage Management**).

Requires **ERPNext** on the site.

---

## Workspace overview

| Section | Purpose |
|---------|---------|
| **Master data** | Trucks, drivers, expense types, **custody types**, customers, settings |
| **1 · Shipping requests** | Customer orders with pickup/delivery locations |
| **2 · Trips** | Operational trips (shipments, truck, driver) — no accounting here |
| **3 · Trip accounting** | List trips → open **accounting sheet** (revenue, expenses, custody) |
| **Reports** | Driver, trip, truck, and custody reports (driver + date filters) |

---

## Suggested workflow

1. Set up **Haulage Logistics Settings**, trucks (by name), drivers (by name), expense and custody types (with ledger accounts).
2. **Shipping Request** → **Haulage Trip** (operational).
3. **Trip accounting** → select trip → allocate **expenses** and **custody**, create invoices / journal entry.
4. Use **Reports** for period analysis by driver, trip, truck, or custody lines.

---

## Whitelisted API

- `haulage_mgmt.haulage_logistics.api.create_sales_invoice_from_shipment`
- `haulage_mgmt.haulage_logistics.api.create_trip_expense_journal_entry`

---

## License

MIT — see `license.txt`.
