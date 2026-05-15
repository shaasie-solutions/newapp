frappe.pages["trip-operations"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Trip operations"),
		single_column: true,
	});

	page.trip_operations = new TripOperationsHub(page);
};

frappe.pages["trip-operations"].on_page_show = function (wrapper) {
	const page = wrapper.page;
	if (page.trip_operations) {
		const view = frappe.route_options?.view;
		if (view) {
			page.trip_operations.set_view(view, false);
		}
		page.trip_operations.refresh();
	}
};

class TripOperationsHub {
	constructor(page) {
		this.page = page;
		this.view = frappe.route_options?.view === "accounting" ? "accounting" : "operations";
		this.make_toolbar();
		this.make_filters();
		this.$body = $('<div class="trip-operations-hub"></div>').appendTo(this.page.main);
		this.refresh();
	}

	make_toolbar() {
		this.page.add_inner_button(__("Operations list"), () => this.set_view("operations"));
		this.page.add_inner_button(__("Trip accounting"), () => this.set_view("accounting"));
		this.page.add_inner_button(__("New Haulage Trip"), () => frappe.new_doc("Haulage Trip"));
	}

	set_view(view, refresh = true) {
		this.view = view === "accounting" ? "accounting" : "operations";
		this.page.set_title(
			this.view === "accounting" ? __("Trip accounting") : __("Trip operations"),
		);
		if (refresh) {
			this.refresh();
		}
	}

	make_filters() {
		this.page.add_field({
			fieldtype: "Select",
			fieldname: "trip_status",
			label: __("Status"),
			options: haulage_mgmt.i18n
				? haulage_mgmt.i18n.trip_status_filter_options()
				: "\nPreparing\nStarted\nPaused\nCompleted\nCancelled",
			change: () => this.refresh(),
		});
		this.page.add_inner_button(__("Refresh"), () => this.refresh());
	}

	refresh() {
		const status = this.page.fields_dict.trip_status?.get_value();
		if (this.view === "accounting") {
			frappe.call({
				method: "haulage_mgmt.haulage_logistics.page.trip_accounting.trip_accounting.get_trip_accounting_list",
				args: { status: status || null },
				freeze: true,
				callback: (r) => this.render_accounting(r.message || []),
			});
			return;
		}
		frappe.call({
			method: "haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations.get_trip_operations_list",
			args: { status: status || null },
			freeze: true,
			callback: (r) => this.render_operations(r.message || []),
		});
	}

	open_trip(trip) {
		frappe.set_route("Form", "Haulage Trip", trip);
	}

	open_accounting(trip) {
		if (haulage_mgmt.trip && haulage_mgmt.trip.open_accounting) {
			haulage_mgmt.trip.open_accounting(trip);
			return;
		}
		frappe.route_options = { haulage_accounting_entry: 1 };
		frappe.set_route("Form", "Haulage Trip", trip);
	}

	status_badge(status) {
		const colors = {
			Preparing: "orange",
			Started: "blue",
			Paused: "yellow",
			Completed: "green",
			Cancelled: "red",
		};
		const color = colors[status] || "grey";
		return `<span class="indicator-pill ${color} filterable ellipsis">${frappe.utils.escape_html(
			__(status || ""),
		)}</span>`;
	}

	render_operations(rows) {
		if (!rows.length) {
			this.$body.html(`<p class="text-muted">${__("No trips found.")}</p>`);
			return;
		}

		let html = `<p class="text-muted">${__(
			"Open a trip to run it (start, pause, arrival, cancel) or switch to Trip accounting for revenue and expenses."
		)}</p>
		<table class="table table-bordered table-hover">
			<thead><tr>
				<th>${__("Trip")}</th>
				<th>${__("Status")}</th>
				<th>${__("Date")}</th>
				<th>${__("Driver")}</th>
				<th>${__("Truck")}</th>
			</tr></thead><tbody>`;

		for (const row of rows) {
			const trip = frappe.utils.escape_html(row.trip);
			html += `<tr class="trip-ops-row" data-trip="${trip}" style="cursor:pointer">
				<td><a href="#" class="trip-ops-open" data-trip="${trip}">${trip}</a></td>
				<td>${this.status_badge(row.trip_status)}</td>
				<td>${row.trip_date || ""}</td>
				<td>${frappe.utils.escape_html(row.driver || "")}</td>
				<td>${frappe.utils.escape_html(row.truck || "")}</td>
			</tr>`;
		}
		html += `</tbody></table>`;
		this.$body.html(html);
		this.bind_row_clicks(".trip-ops-open", ".trip-ops-row", (trip) => this.open_trip(trip));
	}

	render_accounting(rows) {
		if (!rows.length) {
			this.$body.html(`<p class="text-muted">${__("No trips found.")}</p>`);
			return;
		}

		const fmt = (v) => frappe.format(v, { fieldtype: "Currency" });
		let html = `<p class="text-muted">${__(
			"Open the accounting sheet to allocate expenses and custody and review shipment revenue."
		)}</p>
		<table class="table table-bordered table-hover">
			<thead><tr>
				<th>${__("Trip")}</th>
				<th>${__("Status")}</th>
				<th>${__("Date")}</th>
				<th>${__("Driver")}</th>
				<th>${__("Truck")}</th>
				<th class="text-right">${__("Revenue")}</th>
				<th class="text-right">${__("Expenses")}</th>
				<th class="text-right">${__("Custody")}</th>
				<th class="text-right">${__("Net income")}</th>
				<th></th>
			</tr></thead><tbody>`;

		for (const row of rows) {
			const net_class = row.net_income >= 0 ? "text-success" : "text-danger";
			const trip = frappe.utils.escape_html(row.trip);
			html += `<tr class="trip-ops-acct-row" data-trip="${trip}" style="cursor:pointer">
				<td><a href="#" class="trip-ops-acct-open" data-trip="${trip}">${trip}</a></td>
				<td>${this.status_badge(row.trip_status)}</td>
				<td>${row.trip_date || ""}</td>
				<td>${frappe.utils.escape_html(row.driver || "")}</td>
				<td>${frappe.utils.escape_html(row.truck || "")}</td>
				<td class="text-right">${fmt(row.revenue)}</td>
				<td class="text-right">${fmt(row.expenses)}</td>
				<td class="text-right">${fmt(row.custody_total)}</td>
				<td class="text-right ${net_class}"><b>${fmt(row.net_income)}</b></td>
				<td><button type="button" class="btn btn-xs btn-primary trip-ops-acct-open" data-trip="${trip}">${__(
					"Open sheet",
				)}</button></td>
			</tr>`;
		}
		html += `</tbody></table>`;
		this.$body.html(html);
		this.bind_row_clicks(".trip-ops-acct-open", ".trip-ops-acct-row", (trip) => this.open_accounting(trip));
	}

	bind_row_clicks(link_sel, row_sel, opener) {
		const open = (trip) => opener(trip);
		this.$body.find(link_sel).on("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			open($(e.currentTarget).data("trip"));
		});
		this.$body.find(row_sel).on("click", (e) => {
			if ($(e.target).closest("a, button").length) {
				return;
			}
			open($(e.currentTarget).data("trip"));
		});
	}
}
