import duckdb

con = duckdb.connect("taxi.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
con.execute("""
    CREATE OR REPLACE TABLE raw.yellow_tripdata AS
    SELECT * FROM read_parquet('raw/yellow_tripdata_2025-*.parquet');
""")
print(con.execute("SELECT count(*) FROM raw.yellow_tripdata").fetchone()[0], "rows")
con.close()

con = duckdb.connect("taxi.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
con.execute("""
    CREATE OR REPLACE TABLE raw.weather_central_park AS
    SELECT * FROM read_csv('raw/weather_central_park_2025.csv', header=true);
""")
count = con.execute("SELECT count(*) FROM raw.weather_central_park").fetchone()[0]
print(f"Loaded {count} rows into raw.weather_central_park")
con.close()