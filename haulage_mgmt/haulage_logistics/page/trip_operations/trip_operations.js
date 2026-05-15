frappe.pages["trip-operations"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("All Trips"),
		single_column: true,
	});

	page.trip_operations = new TripOperationsPage(page);
};

frappe.pages["trip-operations"].on_page_show = function (wrapper) {
	const page = wrapper.page;
	if (page.trip_operations) {
		page.trip_operations.refresh();
	}
};

class TripOperationsPage {
	constructor(page) {
		this.page = page;
		this.make_filters();
		this.$body = $('<div class="trip-operations-list"></div>').appendTo(this.page.main);
		this.refresh();
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
		this.page.add_inner_button(__("New Haulage Trip"), () => {
			frappe.new_doc("Haulage Trip");
		});
	}

	refresh() {
		const status = this.page.fields_dict.trip_status?.get_value();
		frappe.call({
			method: "haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations.get_trip_operations_list",
			args: { status: status || null },
			freeze: true,
			callback: (r) => {
				this.render(r.message || []);
			},
		});
	}

	open_trip(trip) {
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
		const label = __(status || "");
		return `<span class="indicator-pill ${color} filterable ellipsis">${frappe.utils.escape_html(
			label,
		)}</span>`;
	}

	render(rows) {
		if (!rows.length) {
			this.$body.html(`<p class="text-muted">${__("No trips found.")}</p>`);
			return;
		}

		let html = `<p class="text-muted">${__(
			"Click a trip to open it and use the action buttons (start, pause, arrival, cancel)."
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
			html += `<tr class="trip-operations-row" data-trip="${trip}" style="cursor:pointer">
				<td><a href="#" class="trip-operations-open" data-trip="${trip}">${trip}</a></td>
				<td>${this.status_badge(row.trip_status)}</td>
				<td>${row.trip_date || ""}</td>
				<td>${frappe.utils.escape_html(row.driver || "")}</td>
				<td>${frappe.utils.escape_html(row.truck || "")}</td>
			</tr>`;
		}
		html += `</tbody></table>`;
		this.$body.html(html);

		const open = (trip) => this.open_trip(trip);
		this.$body.find(".trip-operations-open").on("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			open($(e.currentTarget).data("trip"));
		});
		this.$body.find(".trip-operations-row").on("click", (e) => {
			if ($(e.target).closest("a").length) {
				return;
			}
			open($(e.currentTarget).data("trip"));
		});
	}
}
