# NYC Taxi Driver Earnings: Where, When, and Does Weather Matter?

Analysis of 48M NYC yellow taxi trips (2025) joined to Central Park daily weather,
answering where and when a driver should position to maximize earnings per hour.

## Earnings by Weather Condition

```sql by_weather
select * from taxi.earnings_by_weather
```

<BarChart data={by_weather} x=weather_condition y=earnings_per_hour title="Earnings per In-Trip Hour by Weather"/>

A naive comparison makes snowy days look about 6.7% more lucrative per in-trip hour
than dry days, but that gap disappears once you control for the calendar. Regressing
daily earnings on weather while controlling for day-of-week and month, none of the
weather variables are significant: snowfall (p = 0.30), precipitation (p = 0.34), or
temperature (p = 0.67). The apparent weather effect was calendar confounding: the
snowy days in 2025 happened to land on days that were already high-earning for
seasonal and day-of-week reasons.

When you drive matters far more. Every day-of-week and month coefficient is
significant at p < 0.02, with swings up to $9.18/hour by day of week and $14.36/hour
by month.

## Top Earning Zone / Hour Combinations

```sql top
select * from taxi.top_zones
```

<DataTable data={top} rows=15/>

Airport zones lead, with a few late-night Manhattan slots close behind. These are
limited to high-volume slots (500+ trips), so they reflect repeatable opportunities
rather than small-sample outliers where one long fare distorts the average.
