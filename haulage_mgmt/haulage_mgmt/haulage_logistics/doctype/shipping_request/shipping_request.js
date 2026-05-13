frappe.ui.form.on("Shipping Request", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Prepare shipment"),
				() => {
					frappe.route_options = { shipping_request: frm.doc.name };
					frappe.new_doc("Shipment Preparation");
				},
				__("Shipping"),
			);
		}
		if (frm.doc.customer) {
			frm.add_custom_button(
				__("Open customer record"),
				() => frappe.set_route("Form", "Customer", frm.doc.customer),
				__("ERPNext"),
			);
			frm.add_custom_button(__("Sales Invoices"), () => {
				frappe.route_options = { customer: frm.doc.customer };
				frappe.set_route("List", "Sales Invoice");
			}, __("ERPNext"));
		}
	},
});
