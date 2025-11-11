import pandas as pd
from datetime import datetime, timedelta
import random

TASKS_ARRIVAL = [
    "Opening cargo doors", "Opening doors", "Passenger disembarkation", "Unloading catering",
    "Unloading cargo hold", "Removing chocks", "Closing doors",
    "Closing cargo compartments and doors", "Potable water refill", "Refueling",
]
TASKS_DEPARTURE = [
    "Opening doors", "Loading catering", "Passenger boarding", "Refueling",
    "Installing stairs/jet bridges", "Cabin cleaning", "Loading cargo holds",
    "Lavatory service", "Installing chocks",
]

_RNG = random.Random(42)
_BASE_DF = None


def regenerate_mock_data():
    global _BASE_DF
    _BASE_DF = _make_base_df()


def _rand_tail():
    return _RNG.choice(["A", "B", "C", "D"]) + str(_RNG.randint(1000, 9999))


def _rand_flight():
    return _RNG.choice(["TA", "AC", "UA", "KL", "AZ"]) + str(_RNG.randint(100, 999))


def _build_base_rows(num=24) -> pd.DataFrame:
    now = datetime.now().replace(microsecond=0)
    rows = []
    for _ in range(num):
        tail = _rand_tail()
        flt = _rand_flight()

        day_shift = 0 if _RNG.random() < 0.6 else 1
        base_day = now - timedelta(days=day_shift)

        arr_time = base_day - timedelta(minutes=_RNG.randint(30, 180))
        dep_time = base_day + timedelta(minutes=_RNG.randint(30, 180))

        for t in TASKS_ARRIVAL:
            est = _RNG.randint(5, 25)
            mu = int(est * 0.95)
            act = max(1, int(_RNG.gauss(mu, 3)))
            start = arr_time + timedelta(minutes=_RNG.randint(0, 10))
            end = start + timedelta(minutes=act)
            rows.append({
                "flight_number_meridian": flt,
                "airfcraft_meridian": tail,
                "task_name": t,
                "departure_fact_meridian": dep_time,
                "arrival_fact_meridian": arr_time,
                "actual_duration_minutes": act,
                "estimated_duration_minutes": est,
                "started_at": start,
                "completed_at": end,
            })

        for t in TASKS_DEPARTURE:
            est = _RNG.randint(5, 25)
            mu = int(est * 0.95)
            act = max(1, int(_RNG.gauss(mu, 3)))
            start = dep_time - timedelta(minutes=_RNG.randint(10, 30))
            end = start + timedelta(minutes=act)
            rows.append({
                "flight_number_meridian": flt,
                "airfcraft_meridian": tail,
                "task_name": t,
                "departure_fact_meridian": dep_time,
                "arrival_fact_meridian": arr_time,
                "actual_duration_minutes": act,
                "estimated_duration_minutes": est,
                "started_at": start,
                "completed_at": end,
            })
    df = pd.DataFrame(rows)
    for c in ["started_at", "completed_at", "arrival_fact_meridian", "departure_fact_meridian"]:
        df[c] = pd.to_datetime(df[c])
    return df


def _make_base_df() -> pd.DataFrame:
    df = _build_base_rows(16)

    df["duration_text"] = (
            df["started_at"].dt.strftime("%H:%M:%S") + " - " + df["completed_at"].dt.strftime("%H:%M:%S")
    )

    delay_threshold = 1.18
    df["delay_flag"] = (df["actual_duration_minutes"] > (df["estimated_duration_minutes"] * delay_threshold)).astype(
        int)

    flip_mask = (df["delay_flag"] == 1) & (pd.Series([_RNG.random() < 0.4 for _ in range(len(df))], index=df.index))
    df.loc[flip_mask, "delay_flag"] = 0

    return df


def _get_base_df() -> pd.DataFrame:
    global _BASE_DF
    if _BASE_DF is None:
        _BASE_DF = _make_base_df()
    return _BASE_DF


def load_base_df() -> pd.DataFrame:
    return _get_base_df()


def _apply_filters(df: pd.DataFrame, date_choice: str, aircraft_list: list, flight_list: list) -> pd.DataFrame:
    dd = df.copy()

    if date_choice == "Today":
        today = pd.Timestamp("today").normalize()
        dd = dd[(dd["arrival_fact_meridian"].dt.normalize() == today) |
                (dd["departure_fact_meridian"].dt.normalize() == today)]
    elif date_choice == "Yesterday":
        y = (pd.Timestamp("today").normalize() - pd.Timedelta(days=1))
        dd = dd[(dd["arrival_fact_meridian"].dt.normalize() == y) |
                (dd["departure_fact_meridian"].dt.normalize() == y)]

    if aircraft_list:
        dd = dd[dd["airfcraft_meridian"].isin(aircraft_list)]
    if flight_list:
        dd = dd[dd["flight_number_meridian"].isin(flight_list)]

    return dd


def distinct_aircraft(date_choice: str, chosen_flights: list) -> list:
    base = _get_base_df()
    dd = _apply_filters(base, date_choice, [], chosen_flights or [])
    return sorted(dd["airfcraft_meridian"].dropna().unique().tolist())


def distinct_flights(date_choice: str, chosen_aircraft: list) -> list:
    base = _get_base_df()
    dd = _apply_filters(base, date_choice, chosen_aircraft or [], [])
    return sorted(dd["flight_number_meridian"].dropna().unique().tolist())


def pivot_table(selected_table: str, date_choice: str, aircraft_list: list, flight_list: list) -> pd.DataFrame:
    base = _get_base_df()
    dd = _apply_filters(base, date_choice, aircraft_list or [], flight_list or [])

    key_cols = ["airfcraft_meridian", "flight_number_meridian"]

    if selected_table == "departure":
        keep = TASKS_DEPARTURE
        delay_prefix = "Departure_"
        ddf = dd[dd["task_name"].isin(keep)].copy()

    elif selected_table == "arrival":
        keep = TASKS_ARRIVAL
        delay_prefix = "Arrival_"
        ddf = dd[dd["task_name"].isin(keep)].copy()

    else:
        keep = list(set(TASKS_ARRIVAL + TASKS_DEPARTURE))
        delay_prefix = ""
        ddf = dd.copy()

    dur = ddf.pivot_table(
        index=key_cols,
        columns="task_name",
        values="duration_text",
        aggfunc="max"
    ).reset_index()

    if selected_table == "arrival":
        times_df = ddf.groupby(key_cols, as_index=False)["arrival_fact_meridian"].first()
        times_df["Time of Arrival"] = times_df["arrival_fact_meridian"].dt.strftime("%H:%M")
        times_df = times_df.drop(columns=["arrival_fact_meridian"])
        merged = dur.merge(times_df, on=key_cols, how="left")

    elif selected_table == "departure":
        times_df = ddf.groupby(key_cols, as_index=False)["departure_fact_meridian"].first()
        times_df["Time of Departure"] = times_df["departure_fact_meridian"].dt.strftime("%H:%M")
        times_df = times_df.drop(columns=["departure_fact_meridian"])
        merged = dur.merge(times_df, on=key_cols, how="left")

    else:
        times_df = (
            ddf.groupby(key_cols, as_index=False)
            .agg(arrival_fact_meridian=("arrival_fact_meridian", "first"),
                 departure_fact_meridian=("departure_fact_meridian", "first"))
        )
        times_df["Time of Arrival"] = times_df["arrival_fact_meridian"].dt.strftime("%H:%M")
        times_df["Time of Departure"] = times_df["departure_fact_meridian"].dt.strftime("%H:%M")
        times_df = times_df.drop(columns=["arrival_fact_meridian", "departure_fact_meridian"])
        merged = dur.merge(times_df, on=key_cols, how="left")

    flg = ddf.pivot_table(
        index=key_cols,
        columns="task_name",
        values="delay_flag",
        aggfunc="max"
    ).reset_index()

    if delay_prefix:
        flg = flg.rename(columns={c: f"{delay_prefix}{c}_delay" for c in flg.columns if c not in key_cols})
    else:
        flg = flg.rename(columns={c: f"{c}_delay" for c in flg.columns if c not in key_cols})

    merged = merged.merge(flg, on=key_cols, how="left")

    merged = merged.rename(columns={
        "airfcraft_meridian": "Aircraft number",
        "flight_number_meridian": "Flight number",
    })

    first_cols = [c for c in ["Aircraft number", "Flight number"] if c in merged.columns]

    if selected_table == "all":

        if "Time of Arrival" in merged.columns:
            first_cols += ["Time of Arrival"]

        ordered_tasks = TASKS_ARRIVAL + TASKS_DEPARTURE
        seen = set()
        task_cols = []
        for t in ordered_tasks:
            if t in merged.columns and t not in seen:
                task_cols.append(t)
                seen.add(t)

        tod_injected = False
        if "Time of Departure" in merged.columns:
            if "Refueling" in task_cols:
                ref_idx = task_cols.index("Refueling") + 1
                task_cols.insert(ref_idx, "Time of Departure")
                tod_injected = True
            else:

                first_cols += ["Time of Departure"]

        ordered_delays = [f"{t}_delay" for t in ordered_tasks]
        seen_d = set()
        delay_cols = []
        for d in ordered_delays:
            if d in merged.columns and d not in seen_d:
                delay_cols.append(d)
                seen_d.add(d)

        final_cols = first_cols + task_cols + delay_cols

    elif selected_table == "arrival":
        task_cols = [t for t in TASKS_ARRIVAL if t in merged.columns]
        delay_cols = [f"Arrival_{t}_delay" for t in TASKS_ARRIVAL if f"Arrival_{t}_delay" in merged.columns]
        if "Time of Arrival" in merged.columns:
            first_cols += ["Time of Arrival"]
        final_cols = first_cols + task_cols + delay_cols

    else:
        task_cols = [t for t in TASKS_DEPARTURE if t in merged.columns]
        delay_cols = [f"Departure_{t}_delay" for t in TASKS_DEPARTURE if f"Departure_{t}_delay" in merged.columns]
        if "Time of Departure" in merged.columns:
            first_cols += ["Time of Departure"]
        final_cols = first_cols + task_cols + delay_cols

    keep_set = set(final_cols)
    merged = merged[[c for c in merged.columns if c in keep_set]]
    merged = merged[final_cols]

    for col in final_cols:
        if col in merged.columns and col.endswith("_delay"):
            merged[col] = merged[col].fillna(0).astype(int)

    base_info = {"Aircraft number", "Flight number", "Time of Arrival", "Time of Departure"}
    for col in final_cols:
        if col in merged.columns and not col.endswith("_delay") and col not in base_info:
            merged[col] = merged[col].fillna("")

    return merged
