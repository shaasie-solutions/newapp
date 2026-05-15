frappe.listview_settings["Haulage Trip"] = {
	get_indicator(doc) {
		const colors = {
			Preparing: "orange",
			Started: "blue",
			Paused: "yellow",
			Completed: "green",
			Cancelled: "red",
		};
		const status = doc.trip_status || "";
		return [__(status), colors[status] || "grey", `trip_status,=,${status}`];
	},
	formatters: {
		trip_status(value) {
			return __(value);
		},
	},
};
