"""Write the small tables the Evidence dashboard reads (reports/sources/taxi/marts.duckdb)."""
import duckdb
import numpy as np
import pandas as pd

from taxi import config
from taxi.features import load_panel

SHOWCASE_ZONES = [161, 138, 132, 79, 230, 181]
SHOWCASE_MODELS = ["seasonal_naive", "lightgbm", "mlp", "gru"]


def demand_pressure(preds, panel, fold):
    """Forecast pickups per cab that dropped off the hour before. No driver IDs, so it's rough."""
    # fares from before the test month only
    start = pd.Timestamp(f"{fold}-01")
    hist = panel[panel.hour_at < start]
    fares = hist.groupby(["zone_id", "day_of_week", "hour_of_day"], as_index=False)[["earnings", "pickups"]].sum()
    fares["earnings_per_trip"] = fares.earnings / fares.pickups.replace(0, np.nan)

    p = preds[(preds.model == "lightgbm") & (preds.horizon == 1) & (preds.fold == fold)]
    prev = panel[["zone_id", "hour_at", "dropoffs"]].copy()
    prev["hour_at"] += pd.Timedelta(hours=1)
    p = p.merge(prev, on=["zone_id", "hour_at"])
    p["day_of_week"] = (p.hour_at.dt.dayofweek + 1) % 7
    p["hour_of_day"] = p.hour_at.dt.hour
    slots = p.groupby(["zone_id", "day_of_week", "hour_of_day"], as_index=False).agg(
        forecast_pickups=("yhat", "mean"), dropoffs_prev_hour=("dropoffs", "mean"))
    slots = slots.merge(fares[["zone_id", "day_of_week", "hour_of_day", "earnings_per_trip"]],
                        on=["zone_id", "day_of_week", "hour_of_day"], how="left")
    slots["pickups_per_arriving_cab"] = slots.forecast_pickups / (slots.dropoffs_prev_hour + 1)
    slots["dollars_per_arriving_cab"] = slots.pickups_per_arriving_cab * slots.earnings_per_trip
    return slots


def run(db_path=None):
    art = config.ARTIFACTS
    preds = pd.read_parquet(art / "predictions" / "backtest.parquet")
    last_fold = sorted(preds.fold.unique())[-1]

    con = duckdb.connect(str(db_path or config.DB_PATH), read_only=True)
    zones = con.sql("select zone_id, zone_name, borough, service_zone from dim_zones").df()
    con.close()
    panel = load_panel(db_path)

    tables = {
        "model_scores": pd.read_csv(art / "metrics_overall.csv"),
        "model_scores_by_fold": pd.read_csv(art / "metrics_by_fold.csv"),
        "model_scores_by_segment": pd.read_csv(art / "metrics_by_segment.csv"),
        "model_comparisons": pd.read_csv(art / "model_comparisons.csv"),
        "lightgbm_importance": pd.read_csv(art / "lightgbm_importance.csv"),
        "weather_effects": pd.read_csv(art / "weather_effects.csv"),
        "rain_hour_profile": pd.read_csv(art / "rain_hour_profile.csv"),
    }

    show = preds[(preds.fold == last_fold) & (preds.horizon == 1) & preds.model.isin(SHOWCASE_MODELS)
                 & preds.zone_id.isin(SHOWCASE_ZONES)]
    cutoff = show.hour_at.min() + pd.Timedelta(days=14)
    show = show[show.hour_at < cutoff]
    wide = show.pivot_table(index=["zone_id", "hour_at", "y"], columns="model", values="yhat").reset_index()
    tables["forecast_showcase"] = wide.merge(zones[["zone_id", "zone_name"]], on="zone_id")

    emb = pd.read_csv(art / "zone_embeddings.csv", index_col="zone_id")
    x = emb.to_numpy() - emb.to_numpy().mean(axis=0)
    xy = x @ np.linalg.svd(x, full_matrices=False)[2][:2].T
    tables["zone_embeddings_2d"] = pd.DataFrame({"zone_id": emb.index, "pc1": xy[:, 0], "pc2": xy[:, 1]}).merge(zones)

    slots = demand_pressure(preds, panel, last_fold)
    tables["demand_pressure"] = slots.merge(zones[["zone_id", "zone_name", "borough"]], on="zone_id")

    config.REPORT_DB.unlink(missing_ok=True)
    out = duckdb.connect(str(config.REPORT_DB))
    for name, df in tables.items():
        out.register("df", df)
        out.execute(f"create table {name} as select * from df")
        out.unregister("df")
        print(f"{name}: {len(df):,} rows")
    out.close()
