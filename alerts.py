"""Decide when to send an alert.

An alert goes out once when a value crosses its limit, not on every check.
When it drops back below 90% of the limit, a "back to normal" message is sent.
The gap stops the bot from spamming when a value hovers around the limit.
"""

LABELS = {
    "aqi": ("AQI", ""),
    "pm2_5": ("PM2.5", " µg/m³"),
    "pm10": ("PM10", " µg/m³"),
    "nitrogen_dioxide": ("NO₂", " µg/m³"),
    "ozone": ("Ozone", " µg/m³"),
    "sulphur_dioxide": ("SO₂", " µg/m³"),
    "carbon_monoxide": ("CO", " µg/m³"),
}

RECOVER_RATIO = 0.9


def check(readings, thresholds, active):
    """Compare readings with thresholds.

    `active` is the set of pollutants we already alerted about.
    Returns (list of messages, updated set of active alerts).
    """
    messages = []
    active = set(active)

    for name, limit in thresholds.items():
        value = readings.get(name)
        if value is None:
            continue
        label, unit = LABELS.get(name, (name, ""))

        if name not in active and value >= limit:
            active.add(name)
            messages.append(f"🔴 {label} is {value:g}{unit} (your limit: {limit:g})")
        elif name in active and value < limit * RECOVER_RATIO:
            active.remove(name)
            messages.append(f"🟢 {label} is back down to {value:g}{unit}")

    return messages, active


def summary(readings, place):
    """One message with all current values."""
    lines = [f"Air quality in {place} ({readings['time'].replace('T', ' ')})",
             f"AQI {readings['aqi']} – {readings['category']}"]
    for name, (label, unit) in LABELS.items():
        if name != "aqi" and name in readings:
            lines.append(f"{label}: {readings[name]:g}{unit}")
    return "\n".join(lines)
