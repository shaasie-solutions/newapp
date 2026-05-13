app_name = "haulage_mgmt"
app_title = "Haulage Management"
app_publisher = "Haulage Mgmt"
app_description = (
    "Shipping requests, trip preparation, haulage trips, expenses, and ERPNext billing integration."
)
app_email = ""
app_license = "MIT"
app_version = "0.1.0"

required_apps = ["erpnext"]

before_migrate = "haulage_mgmt.install.before_migrate"
after_migrate = "haulage_mgmt.install.after_migrate"

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
    "Shipment Preparation": {
        "on_update": "haulage_mgmt.haulage_logistics.doctype.shipment_preparation.shipment_preparation.sync_shipping_request_status",
        "after_insert": "haulage_mgmt.haulage_logistics.doctype.shipment_preparation.shipment_preparation.sync_shipping_request_status",
    },
}

fixtures = []
