import duckdb

con = duckdb.connect()
src = "read_parquet('raw/yellow_tripdata_2026-01.parquet')"

print("Schema:")
con.sql(f"DESCRIBE SELECT * FROM {src}").show()

print("Row count:")
con.sql(f"SELECT count(*) AS rows FROM {src}").show()

print("Garbage check:")
con.sql(f"""
SELECT
  count(*) FILTER (WHERE fare_amount < 0)        AS negative_fares,
  count(*) FILTER (WHERE trip_distance = 0)       AS zero_distance,
  count(*) FILTER (WHERE total_amount <= 0)       AS nonpositive_total,
  count(*) FILTER (WHERE passenger_count = 0)     AS zero_passengers,
  count(*) FILTER (WHERE tpep_dropoff_datetime = tpep_pickup_datetime) AS time_travel
FROM {src}
""").show()

# Filter for dropoff_at > pickup_at
# make sure driver earnings positive
# driver_earnings = fare_amount + tip_amount + extra
# Limitation that tips documented are credit card only