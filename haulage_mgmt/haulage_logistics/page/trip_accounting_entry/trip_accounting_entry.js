/* Redirect legacy entry route to the accounting form (reliable after bench migrate). */
frappe.pages["trip-accounting-entry"].on_page_load = function () {
	const trip = (frappe.route_options && frappe.route_options.trip) || null;
	if (!trip) {
		frappe.set_route("trip-accounting");
		return;
	}
	frappe.route_options = { haulage_accounting_entry: 1 };
	frappe.set_route("Form", "Haulage Trip", trip);
};
