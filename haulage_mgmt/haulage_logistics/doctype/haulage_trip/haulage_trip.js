frappe.provide("haulage_mgmt.trip");

frappe.ui.form.on("Haulage Trip", {
	onload(frm) {
		if (frm.is_new() && !frm.doc.company) {
			const c = frappe.defaults.get_default("company");
			if (c) {
				frm.set_value("company", c);
			}
		}
	},
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}
		frm.add_custom_button(__("Print dispatch sheet"), () => {
			frappe.set_route("print", frm.doctype, frm.doc.name, "Haulage Trip Dispatch");
		});
		frm.add_custom_button(__("Print shipments sheet"), () => {
			frappe.set_route("print", frm.doctype, frm.doc.name, "Haulage Trip Shipments Sheet");
		});
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
		frm.add_custom_button(__("Start"), () => haulage_mgmt.trip.append_event(frm, "Start"), __("Quick events"));
		frm.add_custom_button(__("Pause"), () => haulage_mgmt.trip.append_event(frm, "Pause"), __("Quick events"));
		frm.add_custom_button(__("Resume"), () => haulage_mgmt.trip.append_event(frm, "Resume"), __("Quick events"));
		frm.add_custom_button(__("Arrival"), () => haulage_mgmt.trip.append_event(frm, "Arrival"), __("Quick events"));
		frm.add_custom_button(__("Return"), () => haulage_mgmt.trip.append_event(frm, "Return"), __("Quick events"));
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

haulage_mgmt.trip.append_event = function (frm, event_type) {
	const row = frappe.model.add_child(frm.doc, "trip_events");
	row.event_type = event_type;
	row.event_datetime = frappe.datetime.now_datetime();
	frm.refresh_field("trip_events");
	frm.save();
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
