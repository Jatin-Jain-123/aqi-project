"""Fetch air quality data and work out the Indian AQI."""

import requests

API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
POLLUTANTS = ["pm2_5", "pm10", "nitrogen_dioxide", "ozone", "sulphur_dioxide", "carbon_monoxide"]

# CPCB breakpoints for 24-hour averages: (low conc, high conc, low index, high index)
PM25_BREAKPOINTS = [(0, 30, 0, 50), (30, 60, 51, 100), (60, 90, 101, 200),
                    (90, 120, 201, 300), (120, 250, 301, 400), (250, 380, 401, 500)]
PM10_BREAKPOINTS = [(0, 50, 0, 50), (50, 100, 51, 100), (100, 250, 101, 200),
                    (250, 350, 201, 300), (350, 430, 301, 400), (430, 510, 401, 500)]

CATEGORIES = [(50, "Good"), (100, "Satisfactory"), (200, "Moderate"),
              (300, "Poor"), (400, "Very Poor"), (500, "Severe")]


def fetch(latitude, longitude):
    """Get current pollutant levels plus the last 24 hours of PM data."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(POLLUTANTS),
        "hourly": "pm2_5,pm10",
        "past_hours": 24,
        "forecast_hours": 0,
        "timezone": "Asia/Kolkata",
    }
    response = requests.get(API_URL, params=params, timeout=15)
    response.raise_for_status()
    return parse(response.json())


def parse(data):
    """Turn the raw API response into a flat dict of readings."""
    current = data["current"]
    readings = {name: current[name] for name in POLLUTANTS if current.get(name) is not None}
    readings["time"] = current["time"]

    pm25_avg = average(data["hourly"]["pm2_5"])
    pm10_avg = average(data["hourly"]["pm10"])
    readings["aqi"] = indian_aqi(pm25_avg, pm10_avg)
    readings["category"] = category(readings["aqi"])
    return readings


def average(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def sub_index(concentration, breakpoints):
    """Linear interpolation inside the matching CPCB band."""
    for low_c, high_c, low_i, high_i in breakpoints:
        if concentration <= high_c:
            return round(low_i + (high_i - low_i) * (concentration - low_c) / (high_c - low_c))
    return 500  # off the chart


def indian_aqi(pm25_24h, pm10_24h):
    """AQI is the worst of the sub-indices.

    The official CPCB AQI uses up to 8 pollutants from ground stations. PM2.5
    and PM10 drive it almost every day in Delhi, so this is a close estimate.
    """
    indices = []
    if pm25_24h is not None:
        indices.append(sub_index(pm25_24h, PM25_BREAKPOINTS))
    if pm10_24h is not None:
        indices.append(sub_index(pm10_24h, PM10_BREAKPOINTS))
    return max(indices) if indices else None


def category(aqi):
    if aqi is None:
        return "Unknown"
    for upper, name in CATEGORIES:
        if aqi <= upper:
            return name
    return "Severe"
