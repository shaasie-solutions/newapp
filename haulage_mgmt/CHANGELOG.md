# Changelog

## [0.1.1] — 2026-05-13

### Added

- **`translations/ar.csv`**: Arabic translations (Frappe CSV pattern).
- **`before_uninstall`**: removes **Fleet Manager** role and related **Has Role** rows on site uninstall.

### Changed

- **UI source language English** across DocTypes, workspace, print format, script reports, Python `_("…")`, and client `__(…)`.
- **`MANIFEST.in`**: include `translations/*.csv` for packaging.
- **Company fallback**: first `Company` via `get_all` in `install.py` and Sales Invoice API (replaces empty `get_value` filters).
- **Docs**: monorepo `get-app` path, `bench uninstall-app` / `bench remove-app`, ERPNext prerequisite.

[0.1.1]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.1

## [0.1.0] — 2026-05-13

### Added

- Initial `haulage_mgmt` app for the **Haulage Logistics** module on ERPNext.
- DocTypes: trucks, drivers, shipping routes, expense types, shipping requests, shipment preparation, trips with child tables (shipments, events, expenses).
- Customer link via `Customer`, and Sales Invoice shortcuts from shipping request and trip.
- Reports: trip financial summary, driver performance, truck performance.
- **Haulage Trip Dispatch** print format linked for trips.
- Logistics settings: default freight Item, credit account for trip expense journal.
- Draft Journal Entry from trip expenses, linked on the trip.
- Desk workspace and **Customer** dashboard extension for shipping requests.
- Sync of preparation/request status and truck status (busy/available) with trips.
- Daily scheduled task for fleet document reminders (ToDo).
- **Fleet Manager** role and permissions on relevant DocTypes.

[0.1.0]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.0
