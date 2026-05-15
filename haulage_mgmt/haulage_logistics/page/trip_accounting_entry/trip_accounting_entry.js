frappe.pages["trip-accounting-entry"].on_page_load = function (wrapper) {
	const trip = (frappe.route_options && frappe.route_options.trip) || null;
	if (!trip) {
		frappe.set_route("trip-accounting");
		return;
	}
	delete frappe.route_options.trip;

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Trip accounting") + " — " + trip,
		single_column: true,
	});

	page.add_inner_button(__("Back to trip list"), () => frappe.set_route("trip-accounting"));

	const $host = $('<div class="haulage-trip-accounting-entry-form"></div>').appendTo(page.main);

	frappe.model.with_doctype("Haulage Trip", () => {
		frappe.model.with_doc("Haulage Trip", trip, () => {
			const frm = new frappe.ui.form.Form($host, "Haulage Trip", trip);
			frm.page = page;
			frm._haulage_accounting_entry = true;
		});
	});
};
