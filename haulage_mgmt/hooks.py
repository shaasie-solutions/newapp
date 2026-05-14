app_name = "haulage_mgmt"
app_title = "Haulage Management"
app_publisher = "Haulage Mgmt"
app_description = (
    "Master data, shipping requests, trips, expenses, ERPNext invoices, and script reports."
)
app_email = ""
app_license = "MIT"
app_version = "0.1.13"
app_icon = "truck"
app_logo_url = "/assets/haulage_mgmt/images/haulage-desk.svg"

required_apps = ["erpnext"]

add_to_apps_screen = [
    {
        "name": "haulage_mgmt",
        "logo": app_logo_url,
        "title": "Haulage Management",
        "route": "/desk/haulage-logistics",
        "has_permission": "haulage_mgmt.boot.check_haulage_app_permission",
    }
]

before_migrate = "haulage_mgmt.install.before_migrate"
after_migrate = "haulage_mgmt.install.after_migrate"
before_uninstall = "haulage_mgmt.install.before_uninstall"

override_doctype_dashboards = {
    "Customer": "haulage_mgmt.haulage_logistics.dashboard.customer_dashboard.get_dashboard_data",
}

scheduler_events = {
    "daily": [
        "haulage_mgmt.haulage_logistics.tasks.send_fleet_expiry_reminders",
    ],
}

doc_events = {
    "Haulage Trip": {
        "on_update": "haulage_mgmt.haulage_logistics.doctype.haulage_trip.haulage_trip.on_trip_update",
    },
}

fixtures = []
