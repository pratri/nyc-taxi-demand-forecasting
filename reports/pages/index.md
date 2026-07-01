# NYC Taxi Driver Earnings: Where, When, and Does Weather Matter?

Analysis of 48M NYC yellow taxi trips (2025) joined to Central Park daily weather,
answering where and when a driver should position to maximize earnings per hour.

## Earnings by Weather Condition

```sql by_weather
select * from taxi.earnings_by_weather
```

<BarChart data={by_weather} x=weather_condition y=earnings_per_hour title="Earnings per In-Trip Hour by Weather"/>

Snowy and lightly rainy days show modestly higher earnings per in-trip hour. **Important caveat:**
this is driven partly by shorter trip durations rather than higher per-trip earnings, and rests on
a limited number of weather-distinct days. Direction is suggestive, not causal.

## Top Earning Zone / Hour Combinations

```sql top
select * from taxi.top_zones
```

<DataTable data={top} rows=15/>

Airport zones (132 = JFK, 138 = LaGuardia) dominate, consistent with long high-value airport runs.