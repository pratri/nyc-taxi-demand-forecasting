import requests
from pathlib import Path

url = (
    "https://www.ncei.noaa.gov/access/services/data/v1"
    "?dataset=daily-summaries"
    "&stations=USW00094728"
    "&startDate=2025-01-01"
    "&endDate=2025-12-31"
    "&dataTypes=TMAX,TMIN,PRCP,SNOW,SNWD"
    "&format=csv"
    "&units=standard"
)

raw_dir = Path("raw")
raw_dir.mkdir(exist_ok=True)
dest = raw_dir / "weather_central_park_2025.csv"

print(f"Downloading {url}")
resp = requests.get(url, timeout=60)
resp.raise_for_status()
dest.write_bytes(resp.content)
print(f"Saved to {dest.resolve()} ({dest.stat().st_size} bytes)")
print("--- First few lines ---")
print(dest.read_text()[:500])