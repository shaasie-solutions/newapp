# Changelog

## [0.1.0] — 2026-05-13

### Changed

- Default UI language is **English**; Arabic strings live in **`translations/ar.csv`**. Client strings use `__()`; server messages use `_()`. `MANIFEST.in` includes the `translations` folder for packaging.
- Document monorepo layout, `bench uninstall-app` / `bench remove-app`, and safer default company resolution (`install.py`, Sales Invoice API).
- `before_uninstall` hook removes the **Fleet Manager** role and **Has Role** assignments created by the app.

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
