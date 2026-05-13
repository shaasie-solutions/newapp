# Changelog

## [0.1.6] — 2026-05-13

### Fixed

- **Haulage Trip**: Saving with status **Preparing** no longer resets linked preparation / shipping request from an in-progress state (e.g. after temporarily changing status). **Cancelled** still rolls preparation back to **Ready for Trip** as before.
- **Haulage Trip**: Shipment child rows must always specify a **shipping request** (no blank lines) when the trip is not cancelled.

[0.1.6]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.6

## [0.1.5] — 2026-05-13

### Changed

- **Workspace**: Removed the separate **Analytics** block; **script reports** live only under **8 · Reports**. Reordered shortcuts and link cards to match the operational flow (master data → requests → preparation → trips → ERPNext revenue → reports → settings). Added **Customer**, **New Shipment Preparation**, and **Sales Invoices** shortcuts; link cards are **Master data**, **Shipping & preparation**, **Trips & billing**, **Reports & configuration**.
- **Truck**: Optional **Internal fleet ID** field (alongside naming series / document name).
- **Haulage Trip**: Clearer section labels for execution and expense allocation; **Company** default uses the first `Company` when the user has no default (same pattern as install).
- **Arabic (`ar.csv`)**: New strings for workspace headers and the new labels.

[0.1.5]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.5

## [0.1.4] — 2026-05-13

### Changed

- **Workspace desk UX**: EditorJS `content` with section headers, **shortcut tiles** for every main DocType/report/settings (including **New** forms), and **link cards** (Operations, Fleet & master data, Reports, Configuration). `indicator_color` on workspace; `truck` icon for sidebar/app list.

[0.1.4]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.4

## [0.1.3] — 2026-05-13

### Fixed

- **Workspace 404 (`fleet-haulage`)**: Desk routes slug the workspace **name** (`Haulage Logistics` → `haulage-logistics`), but **title** was `Fleet Haulage` (`fleet-haulage`), so links broke. **Title** now matches **name**; `after_migrate` corrects existing sites and clears a wrong **parent_page** so the item is not nested under another workspace (e.g. Integrations).
- **App launcher**: `add_to_apps_screen` + `app_logo_url` / `app_icon` so **Haulage Management** appears as its own app tile with route `/desk/haulage-logistics` (run `bench build --app haulage_mgmt` after pull).

[0.1.3]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.3

## [0.1.2] — 2026-05-13

### Fixed

- **Bench `get-app` from Git URL:** moved `setup.py`, `MANIFEST.in`, `requirements.txt`, `license.txt`, and `translations/` to the **repository root** so Bench finds `apps/<repo>/setup.py` (fixes `FileNotFoundError: .../newapp/setup.py` when cloning `newapp`).

[0.1.2]: https://github.com/shaasie-solutions/newapp/releases/tag/v0.1.2

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
