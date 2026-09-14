---
title: NYC Taxi Demand Forecasting
---

Forecasts of hourly yellow cab pickups for the 103 zones that make up 99% of
pickups, trained on Jan 2024 to May 2026 TLC trips plus Central Park hourly
weather. All scores are from a rolling backtest: each test month is predicted by
models trained only on data from before that month.

## Forecast error

WAPE = total absolute error / total pickups. 15% means the forecast was off by 15
pickups for every 100 that happened.

```sql scores
select * from taxi.scores order by horizon, wape_pct
```

<DataTable data={scores} rows=30 groupBy=horizon/>

```sql folds
select * from taxi.scores_by_fold
where horizon = 1 and model in ('seasonal_naive', 'how_mean', 'lightgbm', 'gru')
order by fold
```

<LineChart data={folds} x=fold y=wape_pct series=model title="WAPE by test month, 1 hour ahead"/>

The seasonal baselines fall apart in December and January because of the holidays. The trained models hold up much better, but January is still their worst month.

### Are the gaps real?

Difference in WAPE between two models, in percentage points, with a 95% interval
from resampling whole days. If the interval doesn't cross zero, the gap is bigger than day-to-day noise.

```sql comparisons
select * from taxi.comparisons order by horizon, hours, model_a
```

<DataTable data={comparisons} rows=30 groupBy=horizon/>

## Forecast vs actual

```sql showcase_zones
select distinct zone_name from taxi.showcase order by 1
```

<Dropdown data={showcase_zones} name=zone value=zone_name defaultValue="Midtown Center"/>

```sql showcase_zone
select hour_at, y as actual, lightgbm, gru, seasonal_naive
from taxi.showcase
where zone_name = '${inputs.zone.value}'
order by hour_at
```

<LineChart data={showcase_zone} x=hour_at y={['actual', 'lightgbm', 'gru', 'seasonal_naive']} title="Hourly pickups, first two weeks of the last test month"/>

## Where it's worse

```sql segments
select segment_type, segment, model, wape_pct, bias_pct, n
from taxi.scores_by_segment
where horizon = 1 and model in ('seasonal_naive', 'lightgbm', 'gru')
order by segment_type, segment, model
```

<DataTable data={segments} rows=40 groupBy=segment_type/>

```sql importance
select feature, round(h1, 3) as gain_pct from taxi.importance order by h1 desc limit 15
```

<BarChart data={importance} x=feature y=gain_pct sort=false title="LightGBM share of split gain, 1 hour ahead"/>

## Zone embeddings

The MLP learns a 16-number vector per zone. This plots the first two principal
components, colored by TLC service zone. It's one training run, so don't read too much
into it.

```sql embeddings
select * from taxi.embeddings
```

<ScatterPlot data={embeddings} x=pc1 y=pc2 series=service_zone tooltipTitle=zone_name title="Zone embeddings (PCA)"/>

## Rain and pickups

Poisson regression of pickups on rain, snow and temperature bands. The hourly
version has hour-of-week and month effects with standard errors clustered by day;
the daily version sums the same data per day. These are associations with
completed pickups (rain can also mean fewer free cabs).
Changes are in percent.

```sql rain
select "group", granularity, term, level, change, ci_low, ci_high
from taxi.weather_effects
order by "group", granularity desc, term, level
```

<DataTable data={rain} rows=30 groupBy=group/>

```sql rain_profile
select * from taxi.rain_profile order by hour_of_day
```

<LineChart data={rain_profile} x=hour_of_day y=pickups series=wet title="Manhattan core, average pickups per hour"/>

## Where to go next (rough)

Forecast pickups per cab that dropped off in the zone the hour before, times the
typical fare there. TLC data has no driver IDs, so this guesses at competition
rather than measuring wait times.

```sql pressure
select * from taxi.pressure order by dollars_per_arriving_cab desc limit 20
```

<DataTable data={pressure} rows=20/>
