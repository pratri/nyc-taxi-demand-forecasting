import duckdb
con = duckdb.connect("taxi.duckdb")
con.sql("""
    SELECT pickup_location_id, pickup_hour, pickup_dow, trip_count,
           round(earnings_per_hour, 2) AS eph
    FROM main.mart_earnings_by_zone_hour
    WHERE trip_count > 500
    ORDER BY eph DESC
    LIMIT 15
""").show()
con.close()