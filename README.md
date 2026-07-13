# NYC Taxi Driver Earnings: Where, When, and Does Weather Matter?

[![dbt build](https://github.com/pratri/nyc-taxi-analytics/actions/workflows/dbt.yml/badge.svg)](https://github.com/pratri/nyc-taxi-analytics/actions/workflows/dbt.yml)

**[Live dashboard →](https://nyc-taxi-analytics.vercel.app/)**

An analytics engineering project built around one question: where and when should a NYC yellow taxi driver position to maximize earnings per hour, and how much does weather actually move that number?

It takes 48.7M taxi trips, joins them to daily weather, runs them through a layered and tested dbt pipeline, and finishes with a regression that separates the weather effect from calendar effects. The same dbt models run on both DuckDB and BigQuery.

## Headline Finding

Weather has no measurable effect on driver earnings once you control for the calendar. When you drive is what matters.

A naive comparison makes snowy days look 6.7% more lucrative per hour than dry days, but that gap disappears under controls. Regressing daily earnings on weather while controlling for day-of-week and month, none of the weather variables are statistically significant:

| Variable | Coefficient | p-value (HC3 robust) |
|---|---|---|
| Snowfall (in) | +1.17 | 0.30 |
| Precipitation (in) | -0.85 | 0.34 |
| Max temperature (°F) | -0.01 | 0.67 |

The apparent weather effect was calendar confounding: the snowy days in 2025 happened to land on days that were already high-earning for seasonal and day-of-week reasons. The raw weather table even points at the artifact directly — snow has the highest earnings per in-trip hour but the *lowest* earnings per trip, meaning those trips were shorter, not more valuable:

| Condition | Trips | $ / in-trip hour | $ / trip |
|---|--:|--:|--:|
| Snow | 1,618,211 | 88.41 | 22.28 |
| Dry | 29,477,928 | 82.87 | 24.39 |
| Light rain | 5,570,715 | 81.60 | 24.56 |
| Rain | 8,227,048 | 81.19 | 24.28 |

The calendar variables tell a different story. Every day-of-week and month coefficient is significant at p < 0.02, with swings up to $9.18/hour by day of week and $14.36/hour by month. The model explains 59.8% of the variance in daily earnings, almost all of it from those calendar effects.

On location, airport zones lead earnings per hour, with a few late-night Manhattan slots close behind. The best hour/day slot for each of the top zones (limited to slots with 500+ trips, so these are repeatable rather than lucky one-offs):

| Zone | Borough | Best slot | Trips | $ / hour |
|---|---|---|--:|--:|
| LaGuardia Airport | Queens | Mon 12:00 | 10,491 | 271.06 |
| JFK Airport | Queens | Sun 04:00 | 870 | 163.85 |
| East Elmhurst | Queens | Mon 00:00 | 968 | 161.42 |
| Midtown Center | Manhattan | Fri 04:00 | 610 | 154.75 |
| Sutton Place / Turtle Bay North | Manhattan | Sun 00:00 | 3,918 | 151.78 |
| Times Sq / Theatre District | Manhattan | Thu 04:00 | 1,027 | 148.28 |

## Architecture

```
NYC TLC parquet ─┐
NOAA weather CSV ─┼─► raw ─► staging ─► intermediate ─► marts ─► dashboard
TLC zone lookup ─┘                                            └─► regression
```

![dbt lineage graph](docs/lineage.png)

- **staging** — one model per source: rename, cast, deduplicate. Materialized as views.
- **intermediate** — defines a valid revenue trip and driver earnings, and joins weather. Views.
- **marts** — earnings by zone/hour, by weather condition, and a day-level modeling table. Tables.

## Stack

| Tool | Why |
|---|---|
| DuckDB | Reads parquet natively with no load step, aggregates fast on a laptop, needs zero infrastructure |
| dbt | Layered transforms with tests, docs, lineage, and incremental materialization |
| BigQuery | Shows the models port to a cloud warehouse; runs on the free sandbox |
| Evidence.dev | Git-based dashboard, deployed on Vercel |
| statsmodels | Interpretable OLS with robust standard errors |

I started on DuckDB rather than a cloud warehouse on purpose: no billing to worry about, nothing to provision, and a faster edit-run loop. The BigQuery target came later to show the models aren't tied to one engine.

## Data Decisions

Each cleaning rule comes back to the same test: does it change what the driver should do?

**Dropped:**
- Negative-fare rows. These are refunds and chargebacks, not earnings, and not something a driver can position around.
- Trips under one minute long. A real fare divided by near-zero time produces an absurd hourly rate.
- Unknown-location zones 264 and 265. There's no useful recommendation attached to an unknown pickup zone.
- Trips with non-positive driver earnings.

**Kept:**
- Zero-distance trips that still have a real fare and duration. GPS dropouts and very short rides are still paid trips, and this analysis doesn't use `trip_distance`, so a bad value in a column I don't read isn't a reason to drop the row.
- Zero-passenger trips. That field is driver-entered and doesn't affect earnings per hour.

**Earnings definition:** `fare_amount + tip_amount + extra`, leaving out MTA tax, the improvement surcharge, congestion fees, airport fees, and tolls. Those are pass-throughs the driver never keeps, so ranking zones by `total_amount` would partly rank them by how much tax and toll money flows through.

Cleaning removed 3,828,672 of 48,722,602 raw trips (7.9%), leaving 44,893,930 valid trips.

## Data Engineering Notes

**No natural primary key.** The TLC data has no unique identifier, so I hash a surrogate key from trip attributes with `dbt_utils.generate_surrogate_key`.

**The key surfaced real duplicates.** A `unique` test on the surrogate key failed with 5,145 collisions. Digging in, most were distinct trips that happened to match on the original hash columns (fixed by widening the key to nine columns), plus a smaller set of genuine duplicate records (fixed with `row_number()` deduplication). That dedup is what lets the incremental model trust its `unique_key`.

**Incremental loading** on DuckDB processes only trips newer than the current high-water mark. Known limitation: the high-watermark logic misses late-arriving data. A lookback window or a full merge would be the robust fix.

**Data-quality tests.** Singular tests assert positive duration and positive earnings; generic tests assert uniqueness and non-null keys, so the cleaning rules are enforced rather than assumed.

**Portability took real work.** Porting to BigQuery surfaced genuine dialect differences: `EXCLUDE` vs `EXCEPT`, `date_diff` argument order, and `dow` vs `dayofweek` (which also number the days differently). These are handled with dbt's cross-database macros and target conditionals. All 8 models and 10 tests pass on both engines.

## Limitations

- **Earnings per hour uses in-trip time, not shift time.** It measures dollars per hour with a passenger in the car, so it excludes waiting and deadheading. That inflates the rate for low-frequency, high-value slots like early-morning airport pickups. The naive weather "bump" is partly this artifact: snowy days show the *highest* earnings per hour but the *lowest* earnings per trip, meaning the trips were shorter, not more valuable.
- **Cash tips are unobserved.** TLC records credit-card tips only, which biases cash-heavy zones downward.
- **Residuals are heavy-tailed** (skew 5.29, kurtosis 61.8) because of a few anomalous days. I used HC3 robust standard errors; the null weather result holds under both classical and robust inference.
- **The BigQuery run uses one month** (3.7M rows) and materializes staging as a table instead of incrementally, to fit the free sandbox's 10 GB storage cap and lack of DML support. The point is that the models run there, not that the row counts match.
- **Zone rankings are correlational.** High earnings in a zone reflect the trips that started there; they say nothing about the cost of getting to that zone or the competition once you arrive.

## Running It

### Quick start (sample data)

A 100k-row sample of the trip data is committed under `sample_data/`, so the pipeline runs end-to-end in under a minute with no downloads. This is also what CI builds on every push.

```bash
python -m venv .venv && .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/load_sample.py        # sample into sample.duckdb
dbt deps
dbt build --target sample            # 8 models + 10 tests on the sample
```

### Full run

With the same virtualenv active:

```bash
python scripts/download.py           # TLC yellow-taxi parquet, 12 months of 2025
python scripts/download_weather.py   # NOAA Central Park daily summaries
python scripts/download_zones.py     # TLC zone lookup

python scripts/load_raw.py           # trips + weather into DuckDB
python scripts/load_zones.py         # zone lookup into DuckDB

dbt deps
dbt build                            # all models + tests on DuckDB
python scripts/weather_regression.py # OLS with calendar controls

python scripts/export_marts.py       # copy marts into the slim DB Evidence reads
cd reports && npm install && npm run sources && npm run dev
```

Optional BigQuery target: set `GOOGLE_APPLICATION_CREDENTIALS` to a service-account key, then `dbt build --target bigquery`.

## Sources

- [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) — yellow taxi, 2025, parquet
- [NOAA NCEI Daily Summaries](https://www.ncei.noaa.gov/) — Central Park station USW00094728
