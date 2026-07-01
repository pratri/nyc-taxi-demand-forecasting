import duckdb
con = duckdb.connect("taxi.duckdb")

print("Rows with weather attached vs total:")
con.sql("""
    SELECT
        count(*) AS total_trips,
        count(temp_max_f) AS trips_with_weather,
        count(*) - count(temp_max_f) AS trips_missing_weather
    FROM main.int_trips_weather
""").show()

print("Sample with weather:")
con.sql("""
    SELECT cast(pickup_at as date) AS d, driver_earnings, temp_max_f, precip_in, snowfall_in
    FROM main.int_trips_weather
    LIMIT 5
""").show()

con.close()