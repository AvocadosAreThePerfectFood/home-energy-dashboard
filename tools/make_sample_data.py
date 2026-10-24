"""Generate a year of INVENTED data for a fictional home with solar and a battery.

This file does not read any real data. It writes docs/site-data/data.js,
which the dashboard page loads. The numbers are made up and use a fictional
calendar year.
"""
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(2024)  # fixed, so everyone gets the same sample

OUT = Path("docs/site-data/data.js")
DAYS = 365
END_DAY = date(2024, 12, 31)
START_DAY = END_DAY - timedelta(days=DAYS - 1)
OFFLINE = (date(2024, 3, 10), date(2024, 3, 17))  # an invented 8-day outage
WARM_MONTHS = (6, 7, 8, 9)

ARRAY_KW = 6.5
BATTERY_KWH = 13.0
BATTERY_MAX_KW = 5.0
RESERVE = 0.10
EFFICIENCY = 0.95  # each way
STEP_H = 0.25      # 15 minutes
NAMES = ["solar", "home", "grid_import", "grid_export", "charge", "discharge", "soc"]


def bell(hour, center, width):
    return math.exp(-(((hour - center) / width) ** 2))


def simulate_day(day, soc_kwh):
    doy = day.timetuple().tm_yday
    wave = math.sin(2 * math.pi * (doy - 80) / 365)
    day_length = 12.0 + 2.0 * wave
    sunrise = 12.0 - day_length / 2
    sunset = 12.0 + day_length / 2
    sun_scale = 0.78 + 0.22 * wave
    clear = random.random() < 0.75
    weather = random.uniform(0.9, 1.0) if clear else random.uniform(0.25, 0.7)
    heat = max(0.0, math.sin(2 * math.pi * (doy - 110) / 365))
    weekend = 1.15 if day.weekday() >= 5 else 1.0

    steps = []
    for step in range(96):
        hour = (step + 0.5) * STEP_H
        if sunrise < hour < sunset:
            solar = (
                ARRAY_KW * 0.8 * sun_scale * weather
                * math.sin(math.pi * (hour - sunrise) / day_length) ** 1.3
                * random.uniform(0.95, 1.05)
            )
        else:
            solar = 0.0
        home = (
            0.35
            + 0.9 * bell(hour, 7.5, 1.2)
            + 1.6 * bell(hour, 19.0, 1.8)
            + 0.3 * bell(hour, 13.0, 3.0)
            + 2.2 * heat * bell(hour, 16.0, 3.5)
        ) * weekend * max(0.6, random.gauss(1.0, 0.12))

        surplus = solar - home
        charge = discharge = 0.0
        if surplus > 0:
            room = (BATTERY_KWH - soc_kwh) / (STEP_H * EFFICIENCY)
            charge = max(0.0, min(surplus, BATTERY_MAX_KW, room))
            soc_kwh += charge * STEP_H * EFFICIENCY
        elif 16.0 <= hour < 21.0:
            available = max(0.0, soc_kwh - RESERVE * BATTERY_KWH) * EFFICIENCY / STEP_H
            discharge = min(-surplus, BATTERY_MAX_KW, available)
            soc_kwh -= discharge * STEP_H / EFFICIENCY
        grid_import = max(0.0, -surplus - discharge)
        grid_export = max(0.0, surplus - charge)
        steps.append((solar, home, grid_import, grid_export, charge, discharge,
                      100 * soc_kwh / BATTERY_KWH))
    return steps, soc_kwh


def hourly(steps):
    """Average power (kW, equal to kWh per hour) for each of the 24 hours."""
    out = [[0.0] * 24 for _ in NAMES]
    for hour in range(24):
        block = steps[hour * 4:(hour + 1) * 4]
        for k in range(6):
            out[k][hour] = sum(s[k] for s in block) / 4
        out[6][hour] = block[-1][6]  # battery level at the end of the hour
    return out


def main():
    soc = 0.5 * BATTERY_KWH
    daily = []
    detail = {}
    profile = {s: {"n": 0, "series": [[0.0] * 24 for _ in NAMES]} for s in ("warm", "cool")}

    for index in range(DAYS):
        day = START_DAY + timedelta(days=index)
        steps, soc = simulate_day(day, soc)
        if OFFLINE[0] <= day <= OFFLINE[1]:
            daily.append({"date": day.isoformat(), "offline": True})
            continue

        totals = [sum(s[k] for s in steps) * STEP_H for k in range(6)]
        daily.append({
            "date": day.isoformat(),
            "offline": False,
            "solar": round(totals[0], 2),
            "home": round(totals[1], 2),
            "grid_import": round(totals[2], 2),
            "grid_export": round(totals[3], 2),
            "charge": round(totals[4], 2),
            "discharge": round(totals[5], 2),
        })

        per_hour = hourly(steps)
        season = "warm" if day.month in WARM_MONTHS else "cool"
        profile[season]["n"] += 1
        for k in range(7):
            for hour in range(24):
                profile[season]["series"][k][hour] += per_hour[k][hour]
        if day > END_DAY - timedelta(days=14):
            detail[day.isoformat()] = {
                name: [round(v, 2) for v in per_hour[k]] for k, name in enumerate(NAMES)
            }

    profile_out = {}
    for season, acc in profile.items():
        profile_out[season] = {
            name: [round(v / acc["n"], 2) for v in acc["series"][k]]
            for k, name in enumerate(NAMES)
        }

    payload = {
        "meta": {
            "is_sample": True,
            "data_through": END_DAY.isoformat(),
            "note": "Invented data for a fictional home. Not real.",
        },
        "daily": daily,
        "profile": profile_out,
        "detail": detail,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.DASHBOARD_DATA = " + json.dumps(payload, separators=(",", ":")) + ";\n")

    live = [d for d in daily if not d["offline"]]
    print(f"days written: {len(daily)} ({len(daily) - len(live)} offline)")
    for key in ("solar", "home", "grid_import", "grid_export"):
        print(f"  yearly {key}: {sum(d[key] for d in live):,.0f} kWh (invented)")
    print(f"detail days: {len(detail)}")
    print(f"saved: {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
