# NYC Taxi Driver Earnings: Where, When, and Does Weather Matter?

Analysis of 48M NYC yellow taxi trips (2025) joined to Central Park daily weather,
answering where and when a driver should position to maximize earnings per hour.

## Earnings by Weather Condition

```sql by_weather
select * from taxi.earnings_by_weather
```

<BarChart data={by_weather} x=weather_condition y=earnings_per_hour title="Earnings per In-Trip Hour by Weather"/>

Snowy days show ~6.7% higher earnings per in-trip hour than dry days in the raw comparison.
**However, this does not survive controls.** A regression of daily earnings on weather while
controlling for day-of-week and month finds no statistically significant effect of snowfall
(p = 0.30), precipitation (p = 0.34), or temperature (p = 0.67). The apparent weather effect
is calendar confounding: snowy days in 2025 happened to fall on days that were already
high-earning for seasonal and day-of-week reasons.

What actually drives earnings is **when** you drive. Day-of-week swings earnings by up to
$9/hour and month by up to $14/hour, both highly significant.
## Top Earning Zone / Hour Combinations

```sql top
select * from taxi.top_zones
```

<DataTable data={top} rows=15/>

Airport zones (132 = JFK, 138 = LaGuardia) dominate, consistent with long high-value airport runs.