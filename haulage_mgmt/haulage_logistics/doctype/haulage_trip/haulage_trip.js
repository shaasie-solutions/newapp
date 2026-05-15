frappe.provide("haulage_mgmt.trip");

const ACCOUNTING_ROUTE_FLAG = "haulage_accounting_entry";
const ACCOUNTING_RELOAD_KEY = "haulage_trip_accounting_reload";

const ACCOUNTING_FIELDS = [
	"section_break_trip_accounting",
	"trip_revenue_summary",
	"section_break_expenses",
	"trip_expenses",
	"section_break_custodies",
	"trip_custodies",
	"section_break_accounting",
	"trip_journal_entry",
];

const OPERATIONAL_FIELDS = [
	"naming_series",
	"column_break_head",
	"company",
	"truck",
	"driver",
	"departure_date",
	"section_break_shipments",
	"shipments",
];

const ACCOUNTING_HEADER_READONLY = [
	"naming_series",
	"company",
	"truck",
	"driver",
	"departure_date",
];

const TRIP_STATUS_COLORS = {
	Preparing: "orange",
	Started: "blue",
	Paused: "yellow",
	Completed: "green",
	Cancelled: "red",
};

function clear_form_custom_buttons(frm) {
	if (typeof frm.clear_custom_buttons === "function") {
		frm.clear_custom_buttons();
		return;
	}
	if (frm.page && typeof frm.page.clear_custom_actions === "function") {
		frm.page.clear_custom_actions();
	}
}

function enter_accounting_mode(frm) {
	if (!frm.doc.name) {
		return;
	}
	frm._haulage_accounting_entry = true;
}

function mark_accounting_reload(frm) {
	try {
		sessionStorage.setItem(ACCOUNTING_RELOAD_KEY, frm.doc.name);
	} catch (e) {
		/* private browsing */
	}
}

function consume_accounting_reload(frm) {
	try {
		const pending = sessionStorage.getItem(ACCOUNTING_RELOAD_KEY);
		if (pending && pending === frm.doc.name) {
			frm._haulage_accounting_entry = true;
		}
		sessionStorage.removeItem(ACCOUNTING_RELOAD_KEY);
	} catch (e) {
		/* ignore */
	}
}

function sync_accounting_mode_from_route(frm) {
	if (frm.is_new()) {
		frm._haulage_accounting_entry = false;
		return;
	}
	if (frappe.route_options && frappe.route_options[ACCOUNTING_ROUTE_FLAG]) {
		enter_accounting_mode(frm);
		return;
	}
	if (!frm._haulage_accounting_entry) {
		consume_accounting_reload(frm);
	}
}

function is_accounting_entry(frm) {
	return Boolean(frm._haulage_accounting_entry) && !frm.is_new();
}

function set_operational_layout(frm) {
	for (const fieldname of ACCOUNTING_FIELDS) {
		frm.set_df_property(fieldname, "hidden", 1);
	}
	for (const fieldname of OPERATIONAL_FIELDS) {
		frm.set_df_property(fieldname, "hidden", 0);
		frm.set_df_property(fieldname, "read_only", 0);
	}
	if (frm.fields_dict.trip_status) {
		frm.set_df_property("trip_status", "hidden", 1);
	}
}

function set_accounting_entry_layout(frm) {
	for (const fieldname of OPERATIONAL_FIELDS) {
		if (fieldname === "section_break_shipments" || fieldname === "shipments") {
			frm.set_df_property(fieldname, "hidden", 1);
			continue;
		}
		if (ACCOUNTING_HEADER_READONLY.includes(fieldname)) {
			frm.set_df_property(fieldname, "hidden", 0);
			frm.set_df_property(fieldname, "read_only", 1);
			continue;
		}
		frm.set_df_property(fieldname, "hidden", 1);
	}
	for (const fieldname of ACCOUNTING_FIELDS) {
		frm.set_df_property(fieldname, "hidden", 0);
		frm.set_df_property(fieldname, "read_only", fieldname === "trip_journal_entry" ? 1 : 0);
	}
	if (frm.fields_dict.trip_status) {
		frm.set_df_property("trip_status", "hidden", 1);
	}
}

function refresh_accounting_grids(frm) {
	["trip_expenses", "trip_custodies", "trip_revenue_summary"].forEach((fieldname) => {
		if (frm.fields_dict[fieldname]) {
			frm.refresh_field(fieldname);
		}
	});
}

function setup_accounting_entry(frm) {
	set_accounting_entry_layout(frm);
	refresh_accounting_grids(frm);
	frm.dashboard.set_headline_alert(
		__("Trip accounting: allocate expenses and custody, review revenue from shipments."),
		"blue",
	);
	haulage_mgmt.trip.render_revenue_summary(frm);
	haulage_mgmt.trip.add_accounting_buttons(frm);
	if (!frm.is_new()) {
		frm.add_custom_button(__("Back to trip accounting list"), () => {
			frm._haulage_accounting_entry = false;
			frappe.set_route("trip-accounting");
		});
	}
}

function open_trip_accounting_form(trip_name) {
	frappe.route_options = { [ACCOUNTING_ROUTE_FLAG]: 1 };
	frappe.set_route("Form", "Haulage Trip", trip_name);
}

haulage_mgmt.trip.open_accounting = open_trip_accounting_form;

haulage_mgmt.trip.set_status_indicator = function (frm) {
	if (!frm.doc.trip_status) {
		return;
	}
	const color = TRIP_STATUS_COLORS[frm.doc.trip_status] || "grey";
	frm.page.set_indicator(__(frm.doc.trip_status), color);
};

haulage_mgmt.trip.run_status_action = function (frm, action, confirm_message) {
	const run = () => {
		frappe.call({
			method: "haulage_mgmt.haulage_logistics.api.set_trip_status",
			args: { trip_name: frm.doc.name, action },
			freeze: true,
			callback(r) {
				if (!r.exc) {
					frm.reload_doc();
				}
			},
		});
	};
	if (confirm_message) {
		frappe.confirm(confirm_message, run);
		return;
	}
	run();
};

haulage_mgmt.trip.add_status_action_buttons = function (frm) {
	const status = frm.doc.trip_status || "Preparing";
	const group = __("Trip actions");

	if (status === "Preparing" || status === "Paused") {
		frm.add_custom_button(
			__("Start trip"),
			() => haulage_mgmt.trip.run_status_action(frm, "start"),
			group,
		);
	}
	if (status === "Started") {
		frm.add_custom_button(
			__("Pause trip"),
			() => haulage_mgmt.trip.run_status_action(frm, "pause"),
			group,
		);
	}
	if (status === "Started" || status === "Paused") {
		frm.add_custom_button(
			__("Trip arrival"),
			() =>
				haulage_mgmt.trip.run_status_action(
					frm,
					"arrive",
					__("Mark this trip as completed (arrival)?"),
				),
			group,
		);
	}
	if (status !== "Completed" && status !== "Cancelled") {
		frm.add_custom_button(
			__("Cancel trip"),
			() =>
				haulage_mgmt.trip.run_status_action(
					frm,
					"cancel",
					__("Cancel this trip? Linked shipping requests will return to Goods Prepared."),
				),
			group,
		);
	}
};

frappe.ui.form.on("Haulage Trip", {
	onload(frm) {
		sync_accounting_mode_from_route(frm);
		if (frm.is_new() && !frm.doc.company) {
			const c = frappe.defaults.get_user_default("company");
			if (c) {
				frm.set_value("company", c);
			}
		}
	},
	onload_post_render(frm) {
		sync_accounting_mode_from_route(frm);
		if (is_accounting_entry(frm)) {
			setup_accounting_entry(frm);
		} else {
			set_operational_layout(frm);
		}
	},
	refresh(frm) {
		sync_accounting_mode_from_route(frm);
		if (is_accounting_entry(frm)) {
			setup_accounting_entry(frm);
			haulage_mgmt.trip.set_status_indicator(frm);
			return;
		}

		frm._haulage_accounting_entry = false;
		set_operational_layout(frm);
		if (frm.is_new()) {
			frm.page.set_indicator(__("Preparing"), "orange");
			return;
		}

		haulage_mgmt.trip.set_status_indicator(frm);
		haulage_mgmt.trip.add_status_action_buttons(frm);

		frm.add_custom_button(__("Trip accounting"), () => {
			open_trip_accounting_form(frm.doc.name);
		});

		frm.add_custom_button(__("Print dispatch sheet"), () => {
			frappe.set_route("print", frm.doctype, frm.doc.name, "Haulage Trip Dispatch");
		});
		frm.add_custom_button(__("Print shipments sheet"), () => {
			frappe.set_route("print", frm.doctype, frm.doc.name, "Haulage Trip Shipments Sheet");
		});
	},
	after_save(frm) {
		if (is_accounting_entry(frm)) {
			enter_accounting_mode(frm);
			mark_accounting_reload(frm);
			setup_accounting_entry(frm);
		}
	},
});

frappe.ui.form.on("Haulage Trip Shipment", {
	shipping_request(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.shipping_request) {
			frappe.model.set_value(cdt, cdn, "pickup_location", "");
			frappe.model.set_value(cdt, cdn, "delivery_location", "");
			return;
		}
		frappe.db.get_value(
			"Shipping Request",
			row.shipping_request,
			["pickup_location", "delivery_location"],
			(r) => {
				if (!r) {
					return;
				}
				frappe.model.set_value(cdt, cdn, "pickup_location", r.pickup_location || "");
				frappe.model.set_value(cdt, cdn, "delivery_location", r.delivery_location || "");
			},
		);
	},
});

haulage_mgmt.trip.add_accounting_buttons = function (frm) {
	clear_form_custom_buttons(frm);
	frm.add_custom_button(
		__("Create Sales Invoice for shipment"),
		() => haulage_mgmt.trip.prompt_sales_invoice(frm),
		__("Revenue"),
	);
	if (!frm.doc.trip_journal_entry && frm.doc.trip_status !== "Cancelled") {
		frm.add_custom_button(
			__("Create expense journal (draft)"),
			() => haulage_mgmt.trip.create_expense_je(frm),
			__("Accounting"),
		);
	}
	if (frm.doc.trip_journal_entry) {
		frm.add_custom_button(
			__("Open expense journal"),
			() => frappe.set_route("Form", "Journal Entry", frm.doc.trip_journal_entry),
			__("Accounting"),
		);
	}
};

haulage_mgmt.trip.render_revenue_summary = function (frm) {
	if (!frm.doc.name || !frm.fields_dict.trip_revenue_summary) {
		return;
	}
	frappe.call({
		method: "haulage_mgmt.haulage_logistics.page.trip_accounting.trip_accounting.get_trip_accounting_detail",
		args: { trip_name: frm.doc.name },
		callback(r) {
			if (!r.message || !frm.fields_dict.trip_revenue_summary) {
				return;
			}
			const d = r.message;
			frm._haulage_accounting_detail = d;
			const fmt = (v) => frappe.format(v, { fieldtype: "Currency" });
			let rows = "";
			for (const line of d.revenue_lines || []) {
				rows += `<tr>
					<td>${frappe.utils.escape_html(line.shipping_request)}</td>
					<td>${frappe.utils.escape_html(line.customer || "")}</td>
					<td>${frappe.utils.escape_html(line.pickup_location || "")}</td>
					<td>${frappe.utils.escape_html(line.delivery_location || "")}</td>
					<td class="text-right">${fmt(line.agreed_price)}</td>
				</tr>`;
			}
			const net_class = flt(d.net_income) < 0 ? "text-danger" : "text-success";
			const html = `<div class="trip-revenue-summary">
				<p class="text-muted small">${__(
					"Revenue is taken from agreed prices on shipping requests linked to this trip."
				)}</p>
				<table class="table table-bordered table-sm">
					<thead><tr>
						<th>${__("Shipping Request")}</th>
						<th>${__("Customer")}</th>
						<th>${__("Pickup location")}</th>
						<th>${__("Delivery location")}</th>
						<th class="text-right">${__("Agreed Price")}</th>
					</tr></thead>
					<tbody>${rows || `<tr><td colspan="5" class="text-muted">${__("No shipments on this trip.")}</td></tr>`}</tbody>
					<tfoot>
					<tr><th colspan="4" class="text-right">${__("Total revenue")}</th><th class="text-right">${fmt(d.total_revenue)}</th></tr>
					<tr><th colspan="4" class="text-right">${__("Total expenses")}</th><th class="text-right">${fmt(d.total_expenses)}</th></tr>
					<tr><th colspan="4" class="text-right">${__("Total custody")}</th><th class="text-right">${fmt(d.total_custody)}</th></tr>
					<tr><th colspan="4" class="text-right">${__("Net income")}</th><th class="text-right ${net_class}"><b>${fmt(d.net_income)}</b></th></tr>
					</tfoot>
				</table>
			</div>`;
			$(frm.fields_dict.trip_revenue_summary.wrapper).html(html);
		},
	});
};

haulage_mgmt.trip.create_expense_je = function (frm) {
	frappe.call({
		method: "haulage_mgmt.haulage_logistics.api.create_trip_expense_journal_entry",
		args: { trip_name: frm.doc.name },
		freeze: true,
		freeze_message: __("Creating journal entry..."),
		callback(r) {
			if (!r.exc && r.message && r.message.name) {
				enter_accounting_mode(frm);
				frm.reload_doc().then(() => {
					frappe.set_route("Form", "Journal Entry", r.message.name);
				});
			}
		},
	});
};

haulage_mgmt.trip.prompt_sales_invoice = function (frm) {
	const from_doc = (frm.doc.shipments || []).map((r) => r.shipping_request).filter(Boolean);
	const from_api = (frm._haulage_accounting_detail && frm._haulage_accounting_detail.revenue_lines || []).map(
		(l) => l.shipping_request,
	);
	const requests = [...new Set([...from_doc, ...from_api])];
	if (!requests.length) {
		frappe.msgprint(__("No shipments linked to this trip."));
		return;
	}
	const d = new frappe.ui.Dialog({
		title: __("Select shipping request"),
		fields: [
			{
				fieldname: "shipping_request",
				fieldtype: "Select",
				label: __("Shipping request"),
				options: requests.join("\n"),
				reqd: 1,
			},
		],
		primary_action_label: __("Create draft invoice"),
		primary_action(values) {
			frappe.call({
				method: "haulage_mgmt.haulage_logistics.api.create_sales_invoice_from_shipment",
				args: {
					trip_name: frm.doc.name,
					shipping_request_name: values.shipping_request,
				},
				freeze: true,
				freeze_message: __("Creating invoice..."),
				callback(r) {
					if (!r.exc && r.message && r.message.name) {
						frappe.set_route("Form", "Sales Invoice", r.message.name);
					}
				},
			});
			d.hide();
		},
	});
	d.show();
};
