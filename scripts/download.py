import requests
from pathlib import Path

YEAR = "2025"
raw_dir = Path("raw")
raw_dir.mkdir(exist_ok=True)

for m in range(1, 13):
    ym = f"{YEAR}-{m:02d}"
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{ym}.parquet"
    dest = raw_dir / f"yellow_tripdata_{ym}.parquet"
    if dest.exists():
        print(f"Skip {ym} (already have it)")
        continue
    print(f"Downloading {ym}...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print(f"  saved {dest.stat().st_size/1_000_000:.0f} MB")