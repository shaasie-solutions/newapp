frappe.query_reports["Haulage Truck Report"] = {
	onload(report) {
		haulage_mgmt.report_common.default_period_filters(report);
	},
	formatter: haulage_mgmt.report_common.net_income_formatter,
};
