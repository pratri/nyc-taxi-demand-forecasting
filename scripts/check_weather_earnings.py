import duckdb
con = duckdb.connect("taxi.duckdb")
con.sql("""
    SELECT weather_condition, trip_count,
           round(earnings_per_hour, 2) AS eph,
           round(avg_earnings_per_trip, 2) AS avg_per_trip
    FROM main.mart_earnings_by_weather
    ORDER BY eph DESC
""").show()
con.close()