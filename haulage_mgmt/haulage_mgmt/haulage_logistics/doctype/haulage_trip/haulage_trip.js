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
		frm.add_custom_button(__("طباعة ورقة التشغيل"), () => {
			frappe.set_route("print", frm.doctype, frm.doc.name, "Haulage Trip Dispatch");
		});
		frm.add_custom_button(
			__("إنشاء فاتورة بيع للشحنة"),
			() => haulage_mgmt.trip.prompt_sales_invoice(frm),
			__("الإيرادات"),
		);
		if (!frm.doc.trip_journal_entry && frm.doc.trip_status !== "Cancelled") {
			frm.add_custom_button(
				__("إنشاء قيد مصروفات (مسودة)"),
				() => haulage_mgmt.trip.create_expense_je(frm),
				__("المحاسبة"),
			);
		}
		if (frm.doc.trip_journal_entry) {
			frm.add_custom_button(
				__("فتح قيد المصروفات"),
				() => frappe.set_route("Form", "Journal Entry", frm.doc.trip_journal_entry),
				__("المحاسبة"),
			);
		}
		frm.add_custom_button(__("بدء"), () => haulage_mgmt.trip.append_event(frm, "Start"), __("أحداث سريعة"));
		frm.add_custom_button(__("وقف مؤقت"), () => haulage_mgmt.trip.append_event(frm, "Pause"), __("أحداث سريعة"));
		frm.add_custom_button(__("استئناف"), () => haulage_mgmt.trip.append_event(frm, "Resume"), __("أحداث سريعة"));
		frm.add_custom_button(__("وصول"), () => haulage_mgmt.trip.append_event(frm, "Arrival"), __("أحداث سريعة"));
		frm.add_custom_button(__("رجوع"), () => haulage_mgmt.trip.append_event(frm, "Return"), __("أحداث سريعة"));
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
		freeze_message: __("جاري إنشاء القيد..."),
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
		frappe.msgprint(__("لا توجد شحنات مرتبطة بالرحلة."));
		return;
	}
	const d = new frappe.ui.Dialog({
		title: __("اختر طلب الشحن"),
		fields: [
			{
				fieldname: "shipping_request",
				fieldtype: "Select",
				label: __("طلب الشحن"),
				options: requests.join("\n"),
				reqd: 1,
			},
		],
		primary_action_label: __("إنشاء مسودة فاتورة"),
		primary_action(values) {
			frappe.call({
				method: "haulage_mgmt.haulage_logistics.api.create_sales_invoice_from_shipment",
				args: {
					trip_name: frm.doc.name,
					shipping_request_name: values.shipping_request,
				},
				freeze: true,
				freeze_message: __("جاري إنشاء الفاتورة..."),
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
