"""Step 2: simulate the reservoir with its standard operating policy and measure performance."""
import matplotlib.pyplot as plt

from common import load_system, save, RESULTS

_, balance_calcs, performance, reservoir, flows = load_system()

balance = flows.copy()
balance_calcs.sop_full(reservoir=reservoir, water_flows=balance)

metrics = performance.all_metrics(reservoir, balance)
RESULTS.mkdir(exist_ok=True)
metrics.to_csv(RESULTS / "historical_performance.csv", index=False)
print(metrics.to_string())

storage = balance["Storage (m3)"] / 1e6
full = reservoir.full_lake_volume / 1e6
dead = reservoir.dead_storage / 1e6
print(f"Reservoir full on {(storage >= full - 1e-6).mean():.0%} of days; usable storage {full - dead:.0f} hm3")

window = storage["1962":"1967"]
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(window.index, window, color="tab:blue", lw=1.5, label="Storage")
ax.axhline(full, color="grey", lw=1, ls=":", label="Full")
ax.axhline(dead, color="black", lw=1, ls="--", label="Dead storage")
ax.set_ylabel("Storage (hm³)")
ax.set_title("1962-1967: storage drops every summer and reaches dead storage in 1964 and 1966")
ax.set_ylim(dead - 25, full + 15)
ax.legend(frameon=False, fontsize=9, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.08))
save(fig, "02_drought_storage.png")
