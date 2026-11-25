"""Step 3: multi-objective design of drought measures, from my NSGA-II run (2,000 evaluations, 1962-1967).

NSGA-II is stochastic, so instead of re-running it this script reads the 100 Pareto solutions
saved from my run. The first time, it extracts them from the executed course notebook.
"""
import json
import re

import pandas as pd
import matplotlib.pyplot as plt

from common import course_dir, save, RESULTS

CSV = RESULTS / "pareto_front_nsga2.csv"
LEVERS = ["reduction", "reduction_depth", "lower_intake_depth"]
OBJECTIVES = ["baltimore_vol_rel", "chester_rel", "nuclear_rel"]

if not CSV.exists():
    nb = json.loads((course_dir() / "3-MOEA-optimization.ipynb").read_text(encoding="utf-8"))
    printed = next("".join(o["text"]) for c in nb["cells"] if c["cell_type"] == "code"
                   for o in c.get("outputs", []) if o.get("name") == "stdout" and "Index 0:" in "".join(o["text"]))
    rows = [dict(re.findall(r"(\w+): ([-\d.eE]+)", block)) for block in printed.split("Index ")[1:]]
    front = pd.DataFrame(rows)[LEVERS + OBJECTIVES].astype(float)
    RESULTS.mkdir(exist_ok=True)
    front.to_csv(CSV, index=False)

front = pd.read_csv(CSV)
print(f"{len(front)} Pareto solutions")
print(front[LEVERS + OBJECTIVES].describe().loc[["min", "max"]].round(3).to_string())

rho = front[LEVERS + OBJECTIVES].corr(method="spearman").loc[LEVERS, OBJECTIVES]
rho.round(2).to_csv(RESULTS / "pareto_lever_correlations.csv")
print("\nSpearman correlation, levers vs objectives\n", rho.round(2).to_string())



def non_dominated(points):
    """Boolean mask of points that no other point beats on every objective (all maximised)."""
    keep = []
    for i, p in enumerate(points):
        keep.append(not any((q >= p).all() and (q > p).any() for j, q in enumerate(points) if j != i))
    return pd.Series(keep)


two_obj = non_dominated(front[["baltimore_vol_rel", "nuclear_rel"]].values)
print(f"\nWithout Chester as an objective, {two_obj.sum()} of {len(front)} solutions stay non-dominated")
for col in OBJECTIVES:
    print(f"{col}: range {front[col].max() - front[col].min():.3f}")

# Convergence check. A hand-made design with no demand reduction and the nuclear intake at its
# deepest allowed level was evaluated with the course Tutorial 3 model. Its result is saved in
# results/, because the evaluation function belongs to the course and is not shared here.
check = pd.read_csv(RESULTS / "pareto_convergence_check.csv").set_index("design")
no_action = check.loc["no action", ["baltimore_vol_rel", "chester_rel", "nuclear_rel"]].values
intake_only = check.loc["intake only", ["baltimore_vol_rel", "chester_rel", "nuclear_rel"]].values
values = front[OBJECTIVES].values
dominated = ((intake_only >= values).all(axis=1) & (intake_only > values).any(axis=1)).sum()
print(f"\nNo action: Baltimore {no_action[0]:.3f}, Chester {no_action[1]:.3f}, nuclear {no_action[2]:.3f}")
print(f"Intake only: Baltimore {intake_only[0]:.3f}, Chester {intake_only[1]:.3f}, nuclear {intake_only[2]:.3f}")
print(f"The intake-only design dominates {dominated} of the {len(front)} front members")

fig, ax = plt.subplots(figsize=(7, 5))
sc = ax.scatter(front["baltimore_vol_rel"], front["nuclear_rel"], c=front["chester_rel"], cmap="viridis", s=30)
ax.plot(no_action[0], no_action[2], "X", ms=11, color="tab:red", ls="none", label="No action")
ax.plot(intake_only[0], intake_only[2], "*", ms=16, color="tab:red", mec="white", ls="none",
        label="Deeper intake only")
ax.annotate("Nuclear +11 points,\nBaltimore -0.3 points", xy=(intake_only[0], intake_only[2]),
            xytext=(0.895, 0.950), fontsize=9, arrowprops=dict(arrowstyle="->", color="0.3"))
fig.colorbar(sc, ax=ax, label="Chester reliability")
ax.set_xlabel("Baltimore volumetric reliability")
ax.set_ylabel("Nuclear plant reliability")
ax.set_title("Pareto front of drought measures, 1962-1967")
ax.legend(frameon=False, loc="lower left", numpoints=1)
save(fig, "03_pareto_front.png")
