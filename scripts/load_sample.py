"""Load the committed sample dataset into sample.duckdb.

Lets the whole pipeline run end-to-end without downloading the full 12
months of trip data. Pair it with `dbt build --target sample`. See the
Quick start in the README.
"""
import duckdb

con = duckdb.connect("sample.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

con.execute("""
    CREATE OR REPLACE TABLE raw.yellow_tripdata AS
    SELECT * FROM read_parquet('sample_data/yellow_tripdata_sample.parquet');
""")
con.execute("""
    CREATE OR REPLACE TABLE raw.weather_central_park AS
    SELECT * FROM read_csv('sample_data/weather_central_park_2025.csv', header=true);
""")
con.execute("""
    CREATE OR REPLACE TABLE raw.taxi_zones AS
    SELECT * FROM read_csv('sample_data/taxi_zone_lookup.csv', header=true);
""")

for table in ["yellow_tripdata", "weather_central_park", "taxi_zones"]:
    count = con.execute(f"SELECT count(*) FROM raw.{table}").fetchone()[0]
    print(f"Loaded {count:,} rows into raw.{table}")

con.close()
