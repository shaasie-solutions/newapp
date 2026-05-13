# newapp

Repository containing a **Frappe / ERPNext** app for fleet haulage and shipping logistics.

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

[Semantic Versioning](https://semver.org/) via Git tags (for example `v0.1.0`).
