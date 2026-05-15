frappe.pages["trip-accounting"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Trip Accounting"),
		single_column: true,
	});

	page.trip_accounting = new TripAccountingPage(page);
};

frappe.pages["trip-accounting"].on_page_show = function (wrapper) {
	const page = wrapper.page;
	if (page.trip_accounting) {
		page.trip_accounting.refresh();
	}
};

class TripAccountingPage {
	constructor(page) {
		this.page = page;
		this.make_filters();
		this.$body = $('<div class="trip-accounting-list"></div>').appendTo(this.page.main);
		this.refresh();
	}

	make_filters() {
		this.page.add_field({
			fieldtype: "Select",
			fieldname: "trip_status",
			label: __("Status"),
			options: "\nPreparing\nStarted\nPaused\nCompleted\nCancelled",
			change: () => this.refresh(),
		});
		this.page.add_inner_button(__("Refresh"), () => this.refresh());
	}

	refresh() {
		const status = this.page.fields_dict.trip_status?.get_value();
		frappe.call({
			method: "haulage_mgmt.haulage_logistics.page.trip_accounting.trip_accounting.get_trip_accounting_list",
			args: { status: status || null },
			freeze: true,
			callback: (r) => {
				this.render(r.message || []);
			},
		});
	}

	open_entry(trip) {
		frappe.route_options = { haulage_accounting_entry: 1 };
		frappe.set_route("Form", "Haulage Trip", trip);
	}

	render(rows) {
		if (!rows.length) {
			this.$body.html(`<p class="text-muted">${__("No trips found.")}</p>`);
			return;
		}

		const fmt = (v) => frappe.format(v, { fieldtype: "Currency" });
		let html = `<p class="text-muted">${__(
			"Select a trip to open the accounting sheet (expenses, custody, and revenue)."
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
			html += `<tr class="trip-accounting-row" data-trip="${trip}" style="cursor:pointer">
				<td><a href="#" class="trip-accounting-open" data-trip="${trip}">${trip}</a></td>
				<td>${frappe.utils.escape_html(row.trip_status || "")}</td>
				<td>${row.trip_date || ""}</td>
				<td>${frappe.utils.escape_html(row.driver || "")}</td>
				<td>${frappe.utils.escape_html(row.truck || "")}</td>
				<td class="text-right">${fmt(row.revenue)}</td>
				<td class="text-right">${fmt(row.expenses)}</td>
				<td class="text-right">${fmt(row.custody_total)}</td>
				<td class="text-right ${net_class}"><b>${fmt(row.net_income)}</b></td>
				<td><button type="button" class="btn btn-xs btn-primary trip-accounting-open" data-trip="${trip}">${__(
					"Open sheet"
				)}</button></td>
			</tr>`;
		}
		html += `</tbody></table>`;
		this.$body.html(html);

		const open = (trip) => this.open_entry(trip);
		this.$body.find(".trip-accounting-open").on("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			open($(e.currentTarget).data("trip"));
		});
		this.$body.find(".trip-accounting-row").on("click", (e) => {
			if ($(e.target).closest("a, button").length) {
				return;
			}
			open($(e.currentTarget).data("trip"));
		});
	}
}
