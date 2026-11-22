"""Step 4: stress the system with drier futures.

Compares a uniform 20% flow cut with the Amplified Extremes model, which changes the mean,
the variability and the low flows separately. The last scenario keeps the historical mean
to isolate the effect of the extremes.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common import load_system, save, RESULTS

_, balance_calcs, performance, reservoir, flows = load_system()

# name: (mean, standard deviation, low flow) multipliers; None means a uniform cut
SCENARIOS = {
    "Historical": None,
    "Uniform -20%": "uniform",
    "AE: mean -20%, std x1.5, low x0.6": [0.8, 1.5, 0.6],
    "AE: mean unchanged, std x1.5, low x0.6": [1.0, 1.5, 0.6],
    "AE: mean unchanged, std x1.5": [1.0, 1.5, 1.0],
    "AE: mean unchanged, low x0.6": [1.0, 1.0, 0.6],
}

rows, inflows = [], {}
for name, spec in SCENARIOS.items():
    if spec is None:
        balance = flows.copy()
    elif spec == "uniform":
        balance = balance_calcs.uniform_change_model(flows, 0.8)
    else:
        balance = balance_calcs.amplified_extremes_model(flows_original=flows, model_multipliers=spec, low_quantile=1)
    balance_calcs.sop_full(reservoir=reservoir, water_flows=balance)
    inflows[name] = balance["Total inflows (m3/s)"]
    m = performance.all_metrics(reservoir, balance).set_index("Name")
    rows.append({
        "scenario": name,
        "baltimore_rel": m.loc["Baltimore", "Reliability (0-1)"],
        "chester_rel": m.loc["Chester", "Reliability (0-1)"],
        "nuclear_rel": m.loc["Nuclear", "Reliability (0-1)"],
        "nuclear_failures": m.loc["Nuclear", "Failure count"],
        "env_flow_rel": m.loc["Env. flows", "Reliability (0-1)"],
        "flood_failures": m.loc["Flooding", "Failure count"],
    })

table = pd.DataFrame(rows)
RESULTS.mkdir(exist_ok=True)
table.to_csv(RESULTS / "climate_scenarios.csv", index=False)
print(table.round(3).to_string(index=False))

# Flow duration curves for the three main scenarios
fig, ax = plt.subplots(figsize=(7, 4.5))
for name, color in zip(list(SCENARIOS)[:3], ["black", "tab:blue", "tab:red"]):
    q = np.sort(inflows[name].values)[::-1]
    ax.plot(np.linspace(0, 100, len(q)), q, color=color, lw=1.8, label=name)
ax.set_yscale("log")
ax.set_xlabel("Exceedance probability (%)")
ax.set_ylabel("Inflow (m³/s)")
ax.set_title("Same mean, different extremes")
ax.legend(frameon=False, fontsize=9)
save(fig, "04_flow_duration_curves.png")

# Reliability of the nuclear plant and flood failures across scenarios
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
labels = table["scenario"]
colors = ["black", "tab:blue", "tab:red", "tab:orange", "tab:olive", "tab:purple"]
axes[0].barh(labels, table["nuclear_rel"], color=colors)
axes[0].set_xlim(0.8, 1.0)
axes[0].set_xticks([0.80, 0.85, 0.90, 0.95, 1.00])
axes[0].set_xlabel("Nuclear plant reliability")
axes[1].barh(labels, table["flood_failures"], color=colors)
axes[1].set_xlabel("Flood failures, 1932-2001")
axes[0].invert_yaxis()
fig.suptitle("Changing the extremes hurts more than a uniform 20% cut")
save(fig, "04_scenario_performance.png")
