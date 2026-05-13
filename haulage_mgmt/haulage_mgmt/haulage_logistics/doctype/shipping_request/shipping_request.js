frappe.ui.form.on("Shipping Request", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("تجهيز الشحنة"),
				() => {
					frappe.route_options = { shipping_request: frm.doc.name };
					frappe.new_doc("Shipment Preparation");
				},
				__("الشحن"),
			);
		}
		if (frm.doc.customer) {
			frm.add_custom_button(
				__("فتح بطاقة العميل"),
				() => frappe.set_route("Form", "Customer", frm.doc.customer),
				__("ERPNext"),
			);
			frm.add_custom_button(__("فواتير البيع"), () => {
				frappe.route_options = { customer: frm.doc.customer };
				frappe.set_route("List", "Sales Invoice");
			}, __("ERPNext"));
		}
	},
});
