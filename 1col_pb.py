import os
from datetime import datetime, timezone
from pathlib import Path

import requests

url = "https://api.nationaltransport.ie/gtfsr/v2/gtfsr"
api_key = "24bd6227d16a4383b5b10d32a96b52dc"

response = requests.get(
    url,
    headers={"x-api-key": api_key},
    timeout=30,
)

print("Status:", response.status_code)
response.raise_for_status()

folder = Path("data/ireland_realtime")
folder.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
file_path = folder / f"gtfsr_{timestamp}.pb"

file_path.write_bytes(response.content)

print(f"Saved binary GTFS-Realtime feed to: {file_path}")
print(f"Downloaded bytes: {len(response.content)}")