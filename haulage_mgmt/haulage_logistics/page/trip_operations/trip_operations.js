frappe.pages["trip-operations"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("All Trips"),
		single_column: true,
	});

	page.trip_operations = new TripOperationsHub(page);
};

frappe.pages["trip-operations"].on_page_show = function (wrapper) {
	const page = wrapper.page;
	if (!page.trip_operations) {
		return;
	}
	page.trip_operations.refresh();
};

class TripOperationsHub {
	constructor(page) {
		this.page = page;
		this.make_toolbar();
		this.make_filters();
		this.$body = $('<div class="trip-operations-hub"></div>').appendTo(this.page.main);
		this.refresh();
	}

	make_toolbar() {
		this.page.add_inner_button(__("New Haulage Trip"), () => frappe.new_doc("Haulage Trip"));
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
		frappe.call({
			method:
				"haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations.get_all_trips_hub",
			args: { status: status || null },
			freeze: true,
			freeze_message: __("Loading trips..."),
			callback: (r) => this.render(r.message || []),
		});
	}

	status_badge(status) {
		return haulage_mgmt.i18n ? haulage_mgmt.i18n.status_badge(status) : __(status || "");
	}

	render(rows) {
		if (!rows.length) {
			this.$body.html(`<p class="text-muted">${__("No trips found.")}</p>`);
			return;
		}

		const fmt = (v) => frappe.format(v, { fieldtype: "Currency" });
		let html = `<p class="text-muted">${__(
			"Manage trips from this list: change status, open the trip, or open the accounting sheet for revenue and expenses.",
		)}</p>
		<div class="table-responsive">
		<table class="table table-bordered table-hover trip-ops-table">
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
				<th>${__("Trip actions")}</th>
				<th></th>
			</tr></thead><tbody>`;

		for (const row of rows) {
			const trip = frappe.utils.escape_html(row.trip);
			const net_class = flt(row.net_income) < 0 ? "text-danger" : "text-success";
			const actions = haulage_mgmt.trip.status_actions_for(row.trip_status);
			let action_html = "";
			for (const act of actions) {
				const cls = act.btn_class || "btn-default";
				action_html += `<button type="button" class="btn btn-xs ${cls} trip-ops-status"
					data-trip="${trip}" data-action="${act.action}"
					data-confirm="${frappe.utils.escape_html(act.confirm || "")}">${act.label}</button> `;
			}
			if (!action_html) {
				action_html = `<span class="text-muted">—</span>`;
			}

			html += `<tr class="trip-ops-row" data-trip="${trip}">
				<td><a href="#" class="trip-ops-open" data-trip="${trip}"><b>${trip}</b></a></td>
				<td>${this.status_badge(row.trip_status)}</td>
				<td>${row.trip_date || ""}</td>
				<td>${frappe.utils.escape_html(row.driver || "")}</td>
				<td>${frappe.utils.escape_html(row.truck || "")}</td>
				<td class="text-right">${fmt(row.revenue)}</td>
				<td class="text-right">${fmt(row.expenses)}</td>
				<td class="text-right">${fmt(row.custody_total)}</td>
				<td class="text-right ${net_class}"><b>${fmt(row.net_income)}</b></td>
				<td class="trip-ops-actions">${action_html}</td>
				<td class="text-nowrap">
					<button type="button" class="btn btn-xs btn-default trip-ops-open" data-trip="${trip}">${__(
						"Open",
					)}</button>
					<button type="button" class="btn btn-xs btn-primary trip-ops-acct" data-trip="${trip}">${__(
						"Accounting",
					)}</button>
				</td>
			</tr>`;
		}
		html += `</tbody></table></div>`;
		this.$body.html(html);
		this.bind_events();
	}

	bind_events() {
		const hub = this;

		this.$body.find(".trip-ops-open").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			haulage_mgmt.trip.open_trip($(this).data("trip"));
		});

		this.$body.find(".trip-ops-acct").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			haulage_mgmt.trip.open_accounting($(this).data("trip"));
		});

		this.$body.find(".trip-ops-status").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			const $btn = $(this);
			const trip = $btn.data("trip");
			const action = $btn.data("action");
			const confirm = $btn.data("confirm");
			haulage_mgmt.trip.run_status_action(trip, action, {
				confirm_message: confirm || null,
				on_success: () => hub.refresh(),
			});
		});

		this.$body.find(".trip-ops-row").on("click", function (e) {
			if ($(e.target).closest("a, button").length) {
				return;
			}
			haulage_mgmt.trip.open_trip($(this).data("trip"));
		});
	}
}
