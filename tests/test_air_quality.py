import air_quality


def test_sub_index_band_edges():
    assert air_quality.sub_index(0, air_quality.PM25_BREAKPOINTS) == 0
    assert air_quality.sub_index(30, air_quality.PM25_BREAKPOINTS) == 50
    assert air_quality.sub_index(60, air_quality.PM25_BREAKPOINTS) == 100
    assert air_quality.sub_index(250, air_quality.PM25_BREAKPOINTS) == 400


def test_sub_index_off_the_chart():
    assert air_quality.sub_index(999, air_quality.PM10_BREAKPOINTS) == 500


def test_aqi_is_the_worse_of_pm25_and_pm10():
    # PM2.5 of 75 -> 150, PM10 of 80 -> 81, so PM2.5 decides
    assert air_quality.indian_aqi(75, 80) == 150


def test_categories():
    assert air_quality.category(42) == "Good"
    assert air_quality.category(201) == "Poor"
    assert air_quality.category(450) == "Severe"
    assert air_quality.category(None) == "Unknown"


def test_parse_api_response():
    data = {
        "current": {"time": "2026-10-02T03:30", "pm2_5": 72.6, "pm10": 170.9,
                    "nitrogen_dioxide": 25.9, "ozone": 54.0,
                    "sulphur_dioxide": None, "carbon_monoxide": 460.0},
        "hourly": {"pm2_5": [70, 80, None], "pm10": [150, 170, 160]},
    }
    readings = air_quality.parse(data)
    assert readings["pm2_5"] == 72.6
    assert "sulphur_dioxide" not in readings  # missing values are skipped
    assert readings["aqi"] == 150  # 24h PM2.5 average is 75
    assert readings["category"] == "Moderate"
