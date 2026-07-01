import duckdb
con = duckdb.connect("taxi.duckdb")

print("Row counts:")
con.sql("SELECT count(*) AS staging FROM main.stg_yellow_trips").show()
con.sql("SELECT count(*) AS valid FROM main.int_trips_valid").show()

print("Top earning zone-hours:")
con.sql("""
    SELECT pickup_location_id, pickup_hour, pickup_dow, trip_count, round(earnings_per_hour, 2) AS eph
    FROM main.mart_earnings_by_zone_hour
    WHERE trip_count > 50
    ORDER BY eph DESC
    LIMIT 20
""").show()

con.close()