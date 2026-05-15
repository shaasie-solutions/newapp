frappe.provide("haulage_mgmt.i18n");

/** Translate stored English status / enum values for display (DB value unchanged). */
haulage_mgmt.i18n.status = function (value) {
	return value ? __(value) : "";
};

haulage_mgmt.i18n.trip_statuses = ["Preparing", "Started", "Paused", "Completed", "Cancelled"];

haulage_mgmt.i18n.trip_status_filter_options = function () {
	return "\n" + haulage_mgmt.i18n.trip_statuses.join("\n");
};
