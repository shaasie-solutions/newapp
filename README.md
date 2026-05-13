# newapp

Repository containing a **Frappe / ERPNext** app for fleet haulage and shipping logistics.

The installable app is in **`haulage_mgmt/`** (not at the repo root). Use `bench get-app <path-to-clone>/haulage_mgmt`. See [**Uninstall and removal**](./haulage_mgmt/README.md#uninstall-and-removal) in the app README.

## Contents

| Path | Description |
|------|-------------|
| [`haulage_mgmt/`](./haulage_mgmt/) | Full Frappe app (`haulage_mgmt`) — see the [**app README**](./haulage_mgmt/README.md) for install and setup. |

## Quick start

```bash
cd frappe-bench
bench get-app /path/to/clone/newapp/haulage_mgmt haulage_mgmt
bench --site yoursite.com install-app haulage_mgmt
bench migrate
```

Full workflow, settings, and **language / translations** notes: **`haulage_mgmt/README.md`**.

## Versions

[Semantic Versioning](https://semver.org/) via Git tags (for example `v0.1.0`, `v0.1.1`).
