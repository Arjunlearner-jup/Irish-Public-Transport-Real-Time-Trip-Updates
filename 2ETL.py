from datetime import datetime, timezone
from pathlib import Path
from google.transit import gtfs_realtime_pb2
import pandas as pd

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
INPUT_DIR = Path("data/ireland_realtime")
OUTPUT_DIR = Path("data/ireland_realtime_csv")
OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------------------
# Find latest .pb file (your existing logic)
# ----------------------------------------------------------------------
files = sorted(
    INPUT_DIR.glob("gtfsr_*.pb"),
    key=lambda file: file.stat().st_mtime,
    reverse=True
)

if not files:
    raise FileNotFoundError("No GTFS-Realtime .pb file found")

latest_file = files[0]

# ----------------------------------------------------------------------
# Parse GTFS-Realtime feed
# ----------------------------------------------------------------------
feed = gtfs_realtime_pb2.FeedMessage()

with latest_file.open("rb") as f:
    feed.ParseFromString(f.read())

# ----------------------------------------------------------------------
# Optional: quick counts (your existing logic)
# ----------------------------------------------------------------------
vehicle_count = 0
trip_update_count = 0
alert_count = 0

for entity in feed.entity:
    if entity.HasField("vehicle"):
        vehicle_count += 1
    elif entity.HasField("trip_update"):
        trip_update_count += 1
    elif entity.HasField("alert"):
        alert_count += 1

print("File:", latest_file)
print("Feed timestamp:", feed.header.timestamp)
print("Total entities:", len(feed.entity))
print("Vehicle positions:", vehicle_count)
print("Trip updates:", trip_update_count)
print("Service alerts:", alert_count)

# ----------------------------------------------------------------------
# Helper: Unix timestamp -> ISO string
# ----------------------------------------------------------------------
def ts_to_iso(ts: int | None) -> str | None:
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

# ----------------------------------------------------------------------
# Flatten entities into rows
# ----------------------------------------------------------------------
vehicle_rows = []
trip_update_rows = []
alert_rows = []

for entity in feed.entity:
    eid = entity.id

    # ---------- VehiclePosition ----------
    if entity.HasField("vehicle"):
        v = entity.vehicle
        vehicle_rows.append(
            {
                "entity_id": eid,
                "trip_id": v.trip.trip_id if v.trip.HasField("trip_id") else None,
                "route_id": v.trip.route_id if v.trip.HasField("route_id") else None,
                "trip_start_time": v.trip.start_time or None,
                "trip_start_date": v.trip.start_date or None,
                "trip_schedule_relationship": v.trip.schedule_relationship if v.trip.HasField("schedule_relationship") else None,
                "vehicle_id": v.vehicle.id if v.vehicle.HasField("id") else None,
                "vehicle_label": v.vehicle.label if v.vehicle.HasField("label") else None,
                "vehicle_license_plate": v.vehicle.license_plate if v.vehicle.HasField("license_plate") else None,
                "position_latitude": v.position.latitude if v.position.HasField("latitude") else None,
                "position_longitude": v.position.longitude if v.position.HasField("longitude") else None,
                "position_bearing": v.position.bearing if v.position.HasField("bearing") else None,
                "current_stop_sequence": v.current_stop_sequence if v.HasField("current_stop_sequence") else None,
                "stop_id": v.stop_id if v.HasField("stop_id") else None,
                "current_status": v.current_status if v.HasField("current_status") else None,
                "timestamp": ts_to_iso(v.timestamp) if v.HasField("timestamp") else None,
                "occupancy_status": v.occupancy_status if v.HasField("occupancy_status") else None,
                "occupancy_percentage": v.occupancy_percentage if v.HasField("occupancy_percentage") else None,
            }
        )

    # ---------- TripUpdate ----------
    if entity.HasField("trip_update"):
        tu = entity.trip_update
        base_row = {
            "entity_id": eid,
            "trip_id": tu.trip.trip_id if tu.trip.HasField("trip_id") else None,
            "route_id": tu.trip.route_id if tu.trip.HasField("route_id") else None,
            "trip_start_time": tu.trip.start_time or None,
            "trip_start_date": tu.trip.start_date or None,
            "trip_schedule_relationship": tu.trip.schedule_relationship if tu.trip.HasField("schedule_relationship") else None,
            "trip_update_timestamp": ts_to_iso(tu.timestamp) if tu.HasField("timestamp") else None,
        }

        if tu.stop_time_update:
            for stu in tu.stop_time_update:
                trip_update_rows.append(
                    {
                        **base_row,
                        "stop_sequence": stu.stop_sequence if stu.HasField("stop_sequence") else None,
                        "stop_id": stu.stop_id if stu.HasField("stop_id") else None,
                        "arrival_delay": stu.arrival.delay if stu.HasField("arrival") and stu.arrival.HasField("delay") else None,
                        "arrival_time": ts_to_iso(stu.arrival.time) if stu.HasField("arrival") and stu.arrival.HasField("time") else None,
                        "arrival_uncertainty": stu.arrival.uncertainty if stu.HasField("arrival") and stu.arrival.HasField("uncertainty") else None,
                        "departure_delay": stu.departure.delay if stu.HasField("departure") and stu.departure.HasField("delay") else None,
                        "departure_time": ts_to_iso(stu.departure.time) if stu.HasField("departure") and stu.departure.HasField("time") else None,
                        "departure_uncertainty": stu.departure.uncertainty if stu.HasField("departure") and stu.departure.HasField("uncertainty") else None,
                        "schedule_relationship": stu.schedule_relationship if stu.HasField("schedule_relationship") else None,
                        # No occupancy fields here – not valid on StopTimeUpdate
                    }
                )
        else:
            # Trip-level update only
            trip_update_rows.append(
                {
                    **base_row,
                    "stop_sequence": None,
                    "stop_id": None,
                    "arrival_delay": None,
                    "arrival_time": None,
                    "arrival_uncertainty": None,
                    "departure_delay": None,
                    "departure_time": None,
                    "departure_uncertainty": None,
                    "schedule_relationship": None,
                }
            )

    # ---------- Alert ----------
    if entity.HasField("alert"):
        a = entity.alert
        if a.informed_entity:
            for ie in a.informed_entity:
                alert_rows.append(
                    {
                        "entity_id": eid,
                        "alert_id": a.alert_id if a.HasField("alert_id") else None,
                        "cause": a.cause if a.HasField("cause") else None,
                        "effect": a.effect if a.HasField("effect") else None,
                        "url": a.url.translation[0].text if a.HasField("url") and a.url.translation else None,
                        "header_text": a.header_text.translation[0].text if a.HasField("header_text") and a.header_text.translation else None,
                        "description_text": a.description_text.translation[0].text if a.HasField("description_text") and a.description_text.translation else None,
                        "active_period_start": ts_to_iso(a.active_period[0].start) if a.active_period and a.active_period[0].HasField("start") else None,
                        "active_period_end": ts_to_iso(a.active_period[0].end) if a.active_period and a.active_period[0].HasField("end") else None,
                        "informed_agency_id": ie.agency_id if ie.HasField("agency_id") else None,
                        "informed_route_id": ie.route_id if ie.HasField("route_id") else None,
                        "informed_trip_id": ie.trip.trip_id if ie.HasField("trip") and ie.trip.HasField("trip_id") else None,
                        "informed_stop_id": ie.stop_id if ie.HasField("stop_id") else None,
                        "informed_direction_id": ie.direction_id if ie.HasField("direction_id") else None,
                    }
                )
        else:
            alert_rows.append(
                {
                    "entity_id": eid,
                    "alert_id": a.alert_id if a.HasField("alert_id") else None,
                    "cause": a.cause if a.HasField("cause") else None,
                    "effect": a.effect if a.HasField("effect") else None,
                    "url": None,
                    "header_text": None,
                    "description_text": None,
                    "active_period_start": None,
                    "active_period_end": None,
                    "informed_agency_id": None,
                    "informed_route_id": None,
                    "informed_trip_id": None,
                    "informed_stop_id": None,
                    "informed_direction_id": None,
                }
            )

# ----------------------------------------------------------------------
# Write CSVs
# ----------------------------------------------------------------------
if vehicle_rows:
    df_veh = pd.DataFrame(vehicle_rows)
    out_veh = OUTPUT_DIR / "vehicle_positions.csv"
    df_veh.to_csv(out_veh, index=False)
    print(f"Wrote {len(df_veh)} vehicle rows to {out_veh}")

if trip_update_rows:
    df_tu = pd.DataFrame(trip_update_rows)
    out_tu = OUTPUT_DIR / "trip_updates.csv"
    df_tu.to_csv(out_tu, index=False)
    print(f"Wrote {len(df_tu)} trip update rows to {out_tu}")

if alert_rows:
    df_al = pd.DataFrame(alert_rows)
    out_al = OUTPUT_DIR / "alerts.csv"
    df_al.to_csv(out_al, index=False)
    print(f"Wrote {len(df_al)} alert rows to {out_al}")

if not (vehicle_rows or trip_update_rows or alert_rows):
    print("No VehiclePosition, TripUpdate, or Alert entities found in this .pb file.")