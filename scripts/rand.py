import requests
from pathlib import Path

url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
dest = Path("raw") / "taxi_zone_lookup.csv"
resp = requests.get(url, timeout=60)
resp.raise_for_status()
dest.write_bytes(resp.content)
print(f"Saved {dest} ({dest.stat().st_size} bytes)")