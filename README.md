# NYC Taxi Driver Earnings: Where, When, and Does Weather Matter?

**[Live dashboard →](https://nyc-taxi-analytics.vercel.app/)**

An analytics engineering project answering a concrete question: where and when should a NYC yellow taxi driver position to maximize earnings per hour, and how much does weather move that?

48.7M taxi trips joined to daily weather, transformed through a layered, tested dbt pipeline, with a regression to separate weather effects from calendar confounding. The same dbt models run on both DuckDB and BigQuery.

## Headline Finding

**Weather does not measurably affect driver earnings. Timing does.**

A naive comparison suggests snowy days earn 6.7% more per hour than dry days. That result does not survive controls. Regressing daily earnings on weather while controlling for day-of-week and month, no weather variable is statistically significant:

| Variable | Coefficient | p-value (HC3 robust) |
|---|---|---|
| Snowfall (in) | +1.17 | 0.30 |
| Precipitation (in) | -0.85 | 0.34 |
| Max temperature (°F) | -0.01 | 0.67 |

The apparent weather effect was calendar confounding: snowy days in 2025 happened to fall on days that were already high-earning for seasonal and day-of-week reasons.

What actually drives earnings is **when** you drive. Every day-of-week and month coefficient is significant at p < 0.02, with swings up to **$9.18/hour** by day of week and **$14.36/hour** by month. The model explains 59.8% of variance in daily earnings, almost entirely from calendar effects.

On location: airport zones (LaGuardia, JFK) dominate earnings per hour among high-volume slots.

## Architecture

```
NYC TLC parquet ─┐
NOAA weather CSV ─┼─► raw ─► staging ─► intermediate ─► marts ─► dashboard
TLC zone lookup ─┘                                            └─► regression
```

![dbt lineage graph](docs/lineage.png)

- **staging** — one model per source. Rename, cast, deduplicate. Views.
- **intermediate** — defines a valid revenue trip and driver earnings; joins weather. Views.
- **marts** — earnings by zone/hour, by weather condition, and a day-level modeling table. Tables.

## Stack

| Tool | Why |
|---|---|
| DuckDB | Reads parquet natively, no load step, fast columnar aggregation on a laptop, zero infrastructure |
| dbt | Layered transforms with tests, docs, lineage, and incremental materialization |
| BigQuery | Proves warehouse portability; run on the free sandbox |
| Evidence.dev | Git-based dashboard, deployed on Vercel |
| statsmodels | Interpretable OLS with robust standard errors |

DuckDB was chosen deliberately over starting on a cloud warehouse: no billing risk, no setup tax, faster iteration. Portability was then demonstrated rather than merely claimed.

## Data Decisions

Every cleaning rule traces to one question: does this change what the driver should do?

**Dropped:**
- Negative-fare rows (refunds and chargebacks, not driver earnings, and not something a driver can position to avoid)
- Trips under one minute of duration (produce absurd hourly rates when a real fare divides by near-zero time)
- Unknown-location zones 264 and 265 ("go to the Unknown zone" is not a recommendation)
- Trips with non-positive driver earnings

**Kept:**
- Zero-distance trips with real fare and duration. GPS dropouts and very short rides are real paid trips, and `trip_distance` is not used by this analysis. A garbage value in an unused column is not a reason to discard a row.
- Zero-passenger trips. Driver-entered field, irrelevant to earnings per hour.

**Earnings definition:** `fare_amount + tip_amount + extra`, deliberately excluding MTA tax, improvement surcharge, congestion fees, airport fees, and tolls. These are pass-throughs the driver does not keep. Ranking zones by `total_amount` would partly rank them by tax and toll throughput.

Cleaning removed 3,828,672 of 48,722,602 raw trips (7.9%), leaving 44,893,930 valid trips.

## Data Engineering Notes

**No natural primary key.** The TLC source has no unique identifier, so a surrogate key is hashed from trip attributes via `dbt_utils.generate_surrogate_key`.

**The key surfaced real duplicates.** A `unique` test on the surrogate key failed with 5,145 collisions. Investigation showed most were distinct trips that happened to match on the original hash columns (resolved by widening the key to nine columns) plus a residue of genuine duplicate records (resolved by `row_number()` deduplication). The dedup is what makes the incremental model's `unique_key` trustworthy.

**Incremental loading** on DuckDB, processing only trips newer than the current high-water mark. Known limitation: high-watermark logic misses late-arriving data; a lookback window or full merge would be the robust fix.

**Enforced data quality.** Singular tests assert positive duration and positive earnings; generic tests assert uniqueness and non-null keys. The cleaning rules are checks, not hopes.

**Warehouse portability is real, not free.** Porting to BigQuery surfaced genuine dialect differences: `EXCLUDE` vs `EXCEPT`, `date_diff` argument order, `dow` vs `dayofweek` (with different numbering conventions). These are handled via dbt's cross-database macros and target conditionals. All 8 models and 10 tests pass on both engines.

## Limitations

- **Earnings per hour uses in-trip time, not shift time.** It measures dollars per hour with a passenger, excluding waiting and deadheading. This inflates rates for low-frequency, high-value slots like early-morning airport pickups. The naive weather "bump" is partly this artifact: snowy days show the *highest* earnings per hour but the *lowest* earnings per trip, meaning trips were shorter, not more lucrative.
- **Cash tips are unobserved.** TLC records credit-card tips only, biasing cash-heavy zones downward.
- **Residuals are heavy-tailed** (skew 5.29, kurtosis 61.8) due to anomalous days. HC3 robust standard errors were used; the null weather result is stable under both classical and robust inference.
- **The BigQuery run uses one month** (3.7M rows) and materializes staging as a table rather than incremental, to fit the free sandbox's 10 GB storage cap and lack of DML support. The point demonstrated is that the models run, not that the volumes match.
- **Zone rankings are correlational.** High earnings in a zone reflect trips that started there; they do not account for the cost of getting there or competition from other drivers.

## Running It

```bash
python -m venv .venv && .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/download.py           # TLC parquet, 12 months
python scripts/download_weather.py   # NOAA Central Park daily
python scripts/download_zones.py     # TLC zone lookup
python scripts/load_raw.py
python scripts/load_weather.py
python scripts/load_zones.py

dbt deps
dbt build                            # all models + tests on DuckDB
python scripts/weather_regression.py # OLS with calendar controls

cd reports && npm install && npm run sources && npm run dev
```

Optional BigQuery target: `dbt build --target bigquery`

## Sources

- [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) — yellow taxi, 2025, parquet
- [NOAA NCEI Daily Summaries](https://www.ncei.noaa.gov/) — Central Park station USW00094728