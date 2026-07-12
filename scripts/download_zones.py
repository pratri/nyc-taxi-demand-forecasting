import requests
from pathlib import Path

url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

raw_dir = Path("raw")
raw_dir.mkdir(exist_ok=True)
dest = raw_dir / "taxi_zone_lookup.csv"

print(f"Downloading {url}")
resp = requests.get(url, timeout=60)
resp.raise_for_status()
dest.write_bytes(resp.content)
print(f"Saved to {dest.resolve()} ({dest.stat().st_size} bytes)")
print("--- First few lines ---")
print(dest.read_text()[:300])