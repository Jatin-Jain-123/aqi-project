import alerts

THRESHOLDS = {"aqi": 200, "pm2_5": 90}


def test_alert_when_limit_crossed():
    messages, active = alerts.check({"aqi": 250, "pm2_5": 50}, THRESHOLDS, set())
    assert active == {"aqi"}
    assert len(messages) == 1
    assert "AQI is 250" in messages[0]


def test_no_repeat_alert_while_still_high():
    messages, active = alerts.check({"aqi": 260}, THRESHOLDS, {"aqi"})
    assert messages == []
    assert active == {"aqi"}


def test_no_all_clear_until_clearly_below_limit():
    # 190 is under 200 but above 90% of it (180), so stay quiet
    messages, active = alerts.check({"aqi": 190}, THRESHOLDS, {"aqi"})
    assert messages == []
    assert active == {"aqi"}


def test_all_clear_message():
    messages, active = alerts.check({"aqi": 150}, THRESHOLDS, {"aqi"})
    assert active == set()
    assert "back down to 150" in messages[0]


def test_missing_reading_is_ignored():
    messages, active = alerts.check({}, THRESHOLDS, set())
    assert messages == []
    assert active == set()


def test_summary_lists_values():
    readings = {"time": "2026-10-02T03:30", "aqi": 150, "category": "Moderate",
                "pm2_5": 72.6, "pm10": 170.9}
    text = alerts.summary(readings, "New Delhi")
    assert "AQI 150 – Moderate" in text
    assert "PM2.5: 72.6 µg/m³" in text
