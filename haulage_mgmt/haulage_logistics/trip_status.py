"""Trip status transitions driven by action buttons (not manual select)."""

import frappe
from frappe import _
from frappe.utils import now_datetime

TRIP_STATUS_ACTIONS = {
    "start": {
        "label": _("Start trip"),
        "event": "Start",
        "from": ("Preparing", "Paused"),
        "to": "Started",
        "set_departure": True,
    },
    "pause": {
        "label": _("Pause trip"),
        "event": "Pause",
        "from": ("Started",),
        "to": "Paused",
    },
    "arrive": {
        "label": _("Trip arrival"),
        "event": "Arrival",
        "from": ("Started", "Paused"),
        "to": "Completed",
    },
    "cancel": {
        "label": _("Cancel trip"),
        "event": None,
        "from": ("Preparing", "Started", "Paused"),
        "to": "Cancelled",
    },
}


def apply_trip_status_action(trip, action):
    """Update trip status and optional event log. Caller must save the document."""
    action = (action or "").strip().lower()
    rules = TRIP_STATUS_ACTIONS.get(action)
    if not rules:
        frappe.throw(_("Unknown trip action: {0}").format(action))

    current = trip.trip_status or "Preparing"
    if current not in rules["from"]:
        frappe.throw(
            _("Cannot perform «{0}» while trip status is {1}.").format(
                rules["label"], _(current)
            )
        )

    trip.trip_status = rules["to"]
    if rules.get("set_departure") and not trip.departure_date:
        trip.departure_date = now_datetime()

    event_type = rules.get("event")
    if event_type and frappe.get_meta("Haulage Trip").has_field("trip_events"):
        trip.append(
            "trip_events",
            {"event_type": event_type, "event_datetime": now_datetime()},
        )

    return trip.trip_status
