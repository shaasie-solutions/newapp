frappe.provide("haulage_mgmt.trip");

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

const OPERATIONAL_ONLY = [
	"naming_series",
	"trip_status",
	"column_break_head",
	"company",
	"truck",
	"driver",
	"departure_date",
	"section_break_shipments",
	"shipments",
	"operational_notes",
];

function is_accounting_entry(frm) {
	return Boolean(frm._haulage_accounting_entry);
}

function set_operational_layout(frm) {
	for (const fieldname of ACCOUNTING_FIELDS) {
		frm.set_df_property(fieldname, "hidden", 1);
	}
	for (const fieldname of OPERATIONAL_ONLY) {
		frm.set_df_property(fieldname, "hidden", 0);
	}
}

function set_accounting_entry_layout(frm) {
	for (const fieldname of OPERATIONAL_ONLY) {
		if (fieldname === "section_break_shipments" || fieldname === "shipments") {
			frm.set_df_property(fieldname, "hidden", 1);
			continue;
		}
		if (["naming_series", "trip_status", "company", "truck", "driver", "departure_date"].includes(fieldname)) {
			frm.set_df_property(fieldname, "read_only", 1);
			frm.set_df_property(fieldname, "hidden", 0);
			continue;
		}
		frm.set_df_property(fieldname, "hidden", 1);
	}
	for (const fieldname of ACCOUNTING_FIELDS) {
		frm.set_df_property(fieldname, "hidden", 0);
	}
}

frappe.ui.form.on("Haulage Trip", {
	onload(frm) {
		if (frm.is_new() && !frm.doc.company) {
			const c = frappe.defaults.get_default("company");
			if (c) {
				frm.set_value("company", c);
			}
		}
		if (is_accounting_entry(frm)) {
			set_accounting_entry_layout(frm);
		} else {
			set_operational_layout(frm);
		}
	},
	refresh(frm) {
		if (is_accounting_entry(frm)) {
			set_accounting_entry_layout(frm);
			haulage_mgmt.trip.render_revenue_summary(frm);
			haulage_mgmt.trip.add_accounting_buttons(frm);
			return;
		}

		set_operational_layout(frm);
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Print dispatch sheet"), () => {
			frappe.set_route("print", frm.doctype, frm.doc.name, "Haulage Trip Dispatch");
		});
		frm.add_custom_button(__("Print shipments sheet"), () => {
			frappe.set_route("print", frm.doctype, frm.doc.name, "Haulage Trip Shipments Sheet");
		});
	},
	after_save(frm) {
		if (is_accounting_entry(frm)) {
			haulage_mgmt.trip.render_revenue_summary(frm);
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
	if (!frm.doc.name) {
		return;
	}
	frappe.call({
		method: "haulage_mgmt.haulage_logistics.page.trip_accounting.trip_accounting.get_trip_accounting_detail",
		args: { trip_name: frm.doc.name },
		callback(r) {
			if (!r.message) {
				return;
			}
			const d = r.message;
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
			const html = `<div class="trip-revenue-summary">
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
					<tr><th colspan="4" class="text-right">${__("Net income")}</th><th class="text-right"><b>${fmt(d.net_income)}</b></th></tr>
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
				frm.reload_doc();
				frappe.set_route("Form", "Journal Entry", r.message.name);
			}
		},
	});
};

haulage_mgmt.trip.prompt_sales_invoice = function (frm) {
	const requests = (frm.doc.shipments || []).map((r) => r.shipping_request).filter(Boolean);
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
