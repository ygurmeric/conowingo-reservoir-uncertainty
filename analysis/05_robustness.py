"""Step 5: robustness of four adaptation options across two sets of seven drier futures.

Options:
  L0  current set-up
  L1  nuclear plant intake lowered to the depth of the Baltimore intake
  L2  desalination plant for Baltimore, used whenever the reservoir is not full
  L3  L1 and L2 together
Futures:
  Uniform             inflows cut uniformly by 0, 5, ..., 30%, as in the course tutorial
  Amplified Extremes  mean flow cut by 0, 5, ..., 30%, with variability x1.5 and low flows x0.6,
                      the extreme set-up from step 4
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
FUTURE_SETS = ["Uniform", "Amplified Extremes"]


def future_flows(kind, cut):
    if kind == "Uniform":
        balance = flows.copy()
        balance["Total inflows (m3/s)"] *= 1 - cut / 100
        return balance
    return balance_calcs.amplified_extremes_model(
        flows_original=flows, model_multipliers=[1 - cut / 100, 1.5, 0.6], low_quantile=1)


rows = []
for kind in FUTURE_SETS:
    for cut in CUTS:
        for lever, name in enumerate(LEVERS):
            reservoir = copy.deepcopy(base)
            balance = future_flows(kind, cut)
            if lever in (1, 3):
                reservoir.demand_on_site[2].intake_depth = reservoir.demand_on_site[0].intake_depth
            if lever in (2, 3):
                # Baltimore only draws from the reservoir when it is full; desalination covers the rest
                reservoir.demand_on_site[0].intake_depth = 0.001
            balance = balance_calcs.sop_full(reservoir, balance)
            m = performance.all_metrics(reservoir=reservoir, water_balance=balance).set_index("Name")
            row = {"futures": kind, "flow_cut_pct": cut, "lever": name,
                   "hydropower_gwh": reservoir.daily_production(balance).sum() / 70 / 1000}
            for actor in ACTORS:
                row[f"{actor}_rel"] = m.loc[actor, "Reliability (0-1)"]
                row[f"{actor}_failures_per_year"] = m.loc[actor, "Failure count"] / 70
            rows.append(row)

table = pd.DataFrame(rows)
RESULTS.mkdir(exist_ok=True)
table.to_csv(RESULTS / "robustness_runs.csv", index=False)

# Regret: distance to the best option in the same future, then the worst case over all futures
tables = []
for kind in FUTURE_SETS:
    sub = table[table["futures"] == kind]
    regret = {}
    for actor in ACTORS:
        rel = sub.pivot(index="flow_cut_pct", columns="lever", values=f"{actor}_rel")[LEVERS]
        regret[actor] = (rel.max(axis=1).values[:, None] - rel).max()
    minimax = pd.DataFrame(regret).round(3)
    minimax.insert(0, "futures", kind)
    tables.append(minimax)
    print(f"\nMaximum regret in reliability, {kind} futures\n", minimax.drop(columns="futures").to_string())
pd.concat(tables).to_csv(RESULTS / "robustness_max_regret.csv")

worst = table[table["flow_cut_pct"] == CUTS.max()].pivot(index="lever", columns="futures", values="Nuclear_rel")
print("\nNuclear plant reliability at a 30% cut\n", worst.loc[LEVERS].round(3).to_string())
hp = table.pivot_table(index="flow_cut_pct", columns=["futures", "lever"], values="hydropower_gwh")
print("\nHydropower, GWh per year\n", hp.round(0).to_string())

colors = ["black", "tab:blue", "tab:orange", "tab:green"]
titles = {"Baltimore": "Baltimore, from reservoir", "Nuclear": "Nuclear plant"}
fig, axes = plt.subplots(2, 4, figsize=(14, 7), sharex=True, sharey=True)
for r, kind in enumerate(FUTURE_SETS):
    sub = table[table["futures"] == kind]
    for ax, actor in zip(axes[r], ACTORS):
        for name, color in zip(LEVERS, colors):
            line = sub[sub["lever"] == name]
            ax.plot(line["flow_cut_pct"], line[f"{actor}_rel"], marker="o", ms=3, color=color, label=name)
        if r == 0:
            ax.set_title(titles.get(actor, actor))
        if r == 1:
            ax.set_xlabel("Cut in mean flow (%)")
    axes[r, 0].set_ylabel(f"{kind} futures\nReliability")
axes[0, 0].set_ylim(0.70, 1.0)
fig.legend(*axes[0, 0].get_legend_handles_labels(), frameon=False, ncol=4, loc="lower center",
           bbox_to_anchor=(0.5, -0.04))
fig.suptitle("Reliability of each user under four options, uniform and amplified-extremes futures", y=1.0)
save(fig, "05_robustness.png")
