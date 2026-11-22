"""Step 5: robustness of four adaptation options across seven drier futures.

Options:
  L0  current set-up
  L1  nuclear plant intake lowered to the depth of the Baltimore intake
  L2  desalination plant for Baltimore, used whenever the reservoir is not full
  L3  L1 and L2 together
Futures: inflows cut uniformly by 0, 5, ..., 30%.
"""
import copy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common import load_system, save, RESULTS

_, balance_calcs, performance, base, flows = load_system()

LEVERS = ["L0 current", "L1 deeper nuclear intake", "L2 desalination", "L3 both"]
CUTS = np.arange(0, 35, 5)
ACTORS = ["Baltimore", "Chester", "Nuclear", "Env. flows"]

rows = []
for cut in CUTS:
    for lever, name in enumerate(LEVERS):
        reservoir = copy.deepcopy(base)
        balance = flows.copy()
        balance["Total inflows (m3/s)"] *= 1 - cut / 100
        if lever in (1, 3):
            reservoir.demand_on_site[2].intake_depth = reservoir.demand_on_site[0].intake_depth
        if lever in (2, 3):
            # Baltimore only draws from the reservoir when it is full; desalination covers the rest
            reservoir.demand_on_site[0].intake_depth = 0.001
        balance = balance_calcs.sop_full(reservoir, balance)
        m = performance.all_metrics(reservoir=reservoir, water_balance=balance).set_index("Name")
        row = {"flow_cut_pct": cut, "lever": name,
               "hydropower_gwh": reservoir.daily_production(balance).sum() / 70 / 1000}
        for actor in ACTORS:
            row[f"{actor}_rel"] = m.loc[actor, "Reliability (0-1)"]
            row[f"{actor}_failures_per_year"] = m.loc[actor, "Failure count"] / 70
        rows.append(row)

table = pd.DataFrame(rows)
RESULTS.mkdir(exist_ok=True)
table.to_csv(RESULTS / "robustness_runs.csv", index=False)

# Regret: distance to the best option in the same future, then the worst case over all futures
regret = {}
for actor in ACTORS:
    rel = table.pivot(index="flow_cut_pct", columns="lever", values=f"{actor}_rel")[LEVERS]
    regret[actor] = rel.max(axis=1).values[:, None] - rel
    regret[actor] = regret[actor].max()
minimax = pd.DataFrame(regret).round(3)
minimax.to_csv(RESULTS / "robustness_max_regret.csv")
print("Maximum regret in reliability over all futures, by option and user\n", minimax.to_string())

hp = table.pivot(index="flow_cut_pct", columns="lever", values="hydropower_gwh")[LEVERS]
print("\nHydropower, GWh per year\n", hp.round(0).to_string())

fig, axes = plt.subplots(1, 4, figsize=(14, 3.8), sharex=True)
colors = ["black", "tab:blue", "tab:orange", "tab:green"]
for ax, actor in zip(axes, ACTORS):
    for name, color in zip(LEVERS, colors):
        sub = table[table["lever"] == name]
        ax.plot(sub["flow_cut_pct"], sub[f"{actor}_rel"], marker="o", ms=3, color=color, label=name)
    titles = {"Baltimore": "Baltimore, from reservoir", "Nuclear": "Nuclear plant"}
    ax.set_title(titles.get(actor, actor))
    ax.set_xlabel("Flow reduction (%)")
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter("%.3f"))
fig.subplots_adjust(wspace=0.3)
axes[0].set_ylabel("Reliability")
fig.legend(*axes[0].get_legend_handles_labels(), frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.1))
fig.suptitle("Reliability of each user under seven drier futures and four options", y=1.03)
save(fig, "05_robustness.png")
