import duckdb
import pandas as pd
import statsmodels.formula.api as smf

con = duckdb.connect("taxi.duckdb")
df = con.sql("SELECT * FROM main.mart_daily_earnings").df()
con.close()

print(f"Rows: {len(df)}")
print(df[['earnings_per_hour', 'temp_max_f', 'precip_in', 'snowfall_in']].describe())
print()

# Model: earnings per hour explained by weather, controlling for day of week and month.
# C() makes day_of_week and month categorical (dummy variables), not numeric.
model = smf.ols(
    "earnings_per_hour ~ snowfall_in + precip_in + temp_max_f + C(day_of_week) + C(month)",
    data=df
).fit(cov_type='HC3')

print(model.summary())