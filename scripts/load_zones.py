import duckdb

con = duckdb.connect("taxi.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
con.execute("""
    CREATE OR REPLACE TABLE raw.taxi_zones AS
    SELECT * FROM read_csv('raw/taxi_zone_lookup.csv', header=true);
""")
count = con.execute("SELECT count(*) FROM raw.taxi_zones").fetchone()[0]
print(f"Loaded {count} rows into raw.taxi_zones")
con.close()