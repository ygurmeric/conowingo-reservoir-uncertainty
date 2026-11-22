"""Step 1: is there enough water? Compare the inflow regime with total demand."""
import pandas as pd
import matplotlib.pyplot as plt

from common import load_system, save, RESULTS

_, _, _, reservoir, flows = load_system()

inflow = flows["Total inflows (m3/s)"]
demand = flows[[c for c in flows.columns if c.endswith("demand (m3/s)")]].sum(axis=1)

deficit = inflow < demand
summary = pd.Series({
    "days": len(inflow),
    "deficit_days": int(deficit.sum()),
    "deficit_share": deficit.mean(),
    "mean_inflow_m3s": inflow.mean(),
    "mean_demand_m3s": demand.mean(),
    "inflow_to_demand_ratio": inflow.mean() / demand.mean(),
})
RESULTS.mkdir(exist_ok=True)
summary.to_csv(RESULTS / "inflow_vs_demand.csv", header=["value"])
print(summary.round(3).to_string())

month = inflow.index.month
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.fill_between(range(1, 13), inflow.groupby(month).quantile(0.1), inflow.groupby(month).quantile(0.9),
                color="tab:blue", alpha=0.15, label="Inflow, 10-90% of days")
ax.plot(range(1, 13), inflow.groupby(month).mean(), color="tab:blue", lw=2, label="Mean inflow")
dry = inflow["1964"]
ax.plot(range(1, 13), dry.groupby(dry.index.month).mean(), color="tab:red", lw=2, ls="--", label="Inflow in 1964")
ax.plot(range(1, 13), demand.groupby(month).mean(), color="black", lw=2, label="Total demand")
ax.set_yscale("log")
ax.set_xticks(range(1, 13), list("JFMAMJJASOND"))
ax.set_ylabel("Flow (m³/s)")
ax.set_title("Plenty of water on average, but not in late summer of dry years")
ax.legend(frameon=False, fontsize=9)
save(fig, "01_inflow_vs_demand.png")
