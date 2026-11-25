# Conowingo Reservoir: Drought Measures and Adaptation Under Climate Uncertainty

How reliable is a water supply reservoir today, which drought measures are worth taking, and
how much do the answers change if the climate changes? This project follows these questions for
the **Conowingo reservoir** on the Susquehanna River, which supplies Baltimore, Chester and a
nuclear power plant, and must also meet environmental flows and limit flooding downstream.

The work was done in CE48V, a water resources systems course at Boğaziçi University, in Fall 2026. It uses 70 years of daily
inflow data from 1932 to 2001 and a daily water balance model of the reservoir.

**Methods:** daily water balance simulation · reliability, resilience and vulnerability metrics ·
multi-objective optimisation with NSGA-II · climate scenarios from a flow duration curve model ·
stress testing · regret-based robustness analysis

## Key findings

- **Timing, not quantity, is the problem.** The river carries 7 times more water than all users need,
  but the reservoir can store only about 2 days of mean inflow, so summer droughts empty it.
- **One drought measure is almost free.** A deeper intake raises the nuclear plant's reliability by
  11 points in the 1960s drought and costs Baltimore only 0.3 points.
- **The shape of climate change matters more than its size.** More variable flows with lower low
  flows hurt every user more than a uniform 20% cut, even when the mean flow does not change.
- **Combining a deeper intake with desalination is the robust option.** It has the lowest regret
  in both uniform and amplified-extremes futures, but in the harsher futures no option keeps the
  nuclear plant at today's reliability.

## 1. The problem is timing, not quantity

![Inflow vs demand](figures/01_inflow_vs_demand.png)

On average the river carries **7.1 times** more water than all users need. Still, inflow is below
total demand on **1,254 days, about 5%** of the record, almost all of them from July to October. In
the dry year 1964, inflow falls far below demand from August to November. The reservoir has to
bridge these months, and its usable storage is only **209 hm³**.

## 2. The reservoir is small for its drought

![Storage in the 1960s drought](figures/02_drought_storage.png)

With its standard operating policy the reservoir is full on **93% of days**, but in the 1962-1967
drought it is drawn down every summer and reaches dead storage in 1964 and 1966. The table shows
the three performance measures over the full 1932-2001 record.

| User | Reliability | Failure events | Mean failure length | Vulnerability |
|---|---|---|---|---|
| Baltimore | 0.994 | 8 | 21 days | 100% |
| Chester | 0.980 | 12 | 42 days | 100% |
| Nuclear plant | 0.974 | 17 | 39 days | 100% |
| Environmental flows | 0.998 | 6 | 10 days | 34% |
| Flood protection | 0.9997 | 4 | 2 days | 36% |

- **Reliability** is the share of days without failure. The nuclear plant has the lowest value
  because its intake is the shallowest, so it is the first to fail when the lake level drops.
- **Resilience** shows how fast the system recovers. In the course model it is failure events
  divided by failure days, so its inverse is the mean failure length shown above. Chester and the
  nuclear plant stay without water for about six weeks once they fail.
- **Vulnerability** is the mean worst shortfall of a failure event. For the three water users it is
  100%, because a failure means the lake is below the intake and the supply stops completely. This
  is why reliability alone hides how severe these failures are.
- The reservoir also produces **2,064 GWh** of hydropower per year on average.

## 3. Which drought measures are worth it?

![Pareto front](figures/03_pareto_front.png)

I searched three measures with NSGA-II over the 1962-1967 drought: a demand reduction for
Baltimore, the reservoir level that triggers it, and a deeper intake for the nuclear plant. The
100 Pareto-optimal designs show that:

- **The levers separate cleanly.** The intake depth alone drives the nuclear plant, with a Spearman
  correlation of +0.97, and the demand reduction alone drives Baltimore and Chester, at −0.98 and +0.96.
  One design on the front has no demand reduction and only a deeper intake. It raises the
  plant's reliability from 0.815 to 0.924, while Baltimore stays at 0.927 against 0.930 with no
  action. This is close to a free improvement.
- **The real trade-off is Baltimore against Chester**, and it is a poor one. Baltimore's
  reliability spans 7.2 points across the front, but Chester's spans only 2.0.
- **The framing matters.** Without Chester as an objective, only 17 of the 100 designs stay
  non-dominated. Most of the front exists because of a 2-point difference, which suggests treating
  Chester as a constraint instead of an objective.
- **The search did not fully converge.** I evaluated one design by hand with the same model: no
  demand reduction and the nuclear intake at its deepest allowed level. It gives 0.927 for both
  Baltimore and the nuclear plant and 0.838 for Chester, shown as a star in the figure, and it
  dominates 2 of the 100 designs on the front. With 2,000 evaluations NSGA-II found the right
  region but not the edge of the front, so the front should be read as a good approximation and
  not as the exact optimum.

## 4. A changing climate: the extremes matter more than the mean

![Flow duration curves](figures/04_flow_duration_curves.png)

I compared two ways of building a drier future. The simple way cuts every flow by 20%. The
Amplified Extremes model also cuts the mean by 20%, but makes flows 50% more variable and low flows
40% lower, which fits what we observe in droughts and floods around the world.

![Scenario performance](figures/04_scenario_performance.png)

| Scenario | Baltimore | Chester | Nuclear plant | Flood failures |
|---|---|---|---|---|
| Historical | 0.994 | 0.980 | 0.974 | 4 |
| Uniform −20% | 0.978 | 0.951 | 0.937 | 2 |
| Amplified Extremes, mean −20% | 0.918 | 0.874 | 0.855 | 26 |
| Amplified Extremes, mean unchanged | 0.963 | 0.934 | 0.920 | 27 |

- The uniform model hides the problem. It shows mild water stress and even **fewer** floods, so a
  design checked only against it would look safe.
- Even with **no change in the mean**, more variable flows with lower low flows make every user worse
  off than a uniform 20% drier future, and flood failures rise from 4 to 27.
- Changing only the variability or only the low flows lowers the nuclear plant's reliability to about
  0.96. Changing both lowers it to 0.92, so the two effects add up. The extra floods come from the
  higher variability.

**What this means for decisions:** testing designs against the historical record, or against a
simple change in the mean, gives false confidence. Designs should be stress-tested across many
possible futures, which is what Section 5 does.

## 5. Which adaptation option is robust?

I tested four options: **L0** keeps the current set-up, **L1** lowers the nuclear plant intake to
the depth of the Baltimore intake, **L2** adds a desalination plant that supplies Baltimore whenever
the reservoir is not full, and **L3** combines L1 and L2.

Each option was run in two sets of seven drier futures. In the **uniform** set, as in the course
tutorial, all inflows are cut by 0 to 30%. Section 4 showed that uniform cuts understate the risk, so
I added an **amplified-extremes** set: the mean flow is cut by 0 to 30% as before, but flows are also
50% more variable and low flows 40% lower.

![Robustness of adaptation options](figures/05_robustness.png)

For each future I measured the regret of each option, which is the reliability lost compared with the
best option in that same future. The table shows the worst regret over all seven futures in each set.

| Option | Baltimore, from reservoir | Chester | Nuclear plant | Env. flows |
|---|---|---|---|---|
| *Uniform futures* | | | | |
| L0 current | 0.000 | 0.017 | 0.061 | 0.006 |
| L1 deeper nuclear intake | 0.001 | 0.017 | 0.013 | 0.006 |
| L2 desalination | 0.094 | 0.000 | 0.040 | 0.000 |
| **L3 both** | 0.095 | **0.001** | **0.000** | **0.000** |
| *Amplified-extremes futures* | | | | |
| L0 current | 0.000 | 0.025 | 0.101 | 0.014 |
| L1 deeper nuclear intake | 0.001 | 0.025 | 0.022 | 0.014 |
| L2 desalination | 0.166 | 0.000 | 0.072 | 0.000 |
| **L3 both** | 0.166 | **0.001** | **0.000** | **0.001** |

- **L3 is the robust choice in both sets.** It has zero or almost zero regret for every user except
  Baltimore, so the ranking of the options does not depend on how the futures are built.
- **The size of the risk does depend on it.** With a 30% cut, the nuclear plant's reliability under
  L3 is 0.973 in the uniform futures but only 0.902 in the amplified-extremes futures. Doing nothing
  drops it to 0.801. Regrets are also about twice as large, so choosing the wrong option costs more
  when the extremes grow.
- **Baltimore's loss is not a real shortage.** Under L2 and L3, its reliability only counts water
  taken from the reservoir, and desalination supplies the rest by design. The same metric means
  different things for different users, so regret tables need care.
- **Options help more than one user.** Desalination also raises the nuclear plant's reliability from
  0.974 to 0.982, because the water Baltimore no longer takes stays in the reservoir. The deeper intake
  alone raises it to 0.993, which agrees with the near free improvement found in Section 3.
- **Hydropower depends on the climate, not on the options.** A uniform 30% cut lowers it from 2,064
  to 1,582 GWh per year, and the amplified-extremes futures lower it further, to 1,832 GWh with no
  cut in the mean and 1,272 GWh with a 30% cut, because more water arrives in floods that the
  turbines cannot use. The options change it by less than 0.5%.

The figure uses the same vertical scale in every panel, so the small changes in environmental flows
are shown at their true size.

**Limits:** the analysis ignores the cost and energy use of desalination, and seven futures per set
without probabilities cannot say how likely each outcome is. The amplified-extremes set changes only
the mean, with the variability and low-flow multipliers fixed.

## Next step

Use scenario discovery to vary the mean, variability and low-flow multipliers together and find the
conditions under which each option fails.

## Who did what

| Part | Source |
|---|---|
| Reservoir model, water balance, performance metrics, flow duration curve model, data | Course material, not included in this repository |
| Analysis, interpretation and findings | Mine, developed while working through the course tutorials with help from Claude, an AI assistant |
| Scripts in `analysis/` that rebuild every figure and table | Written by Claude for this repository from my tutorial work; I checked the numbers against my tutorial results |
| The NSGA-II run in `results/pareto_front_nsga2.csv` | Mine, run with the course optimisation set-up |
| The convergence check in Section 3 | Hand-made design from my tutorial answers; script by Claude |
| The scenarios that separate the variability and low-flow effects | Set up and run with Claude, on top of the course climate model |
| The robustness test in Section 5 | Course set-up of options and uniform futures; amplified-extremes futures, script and regret summary by Claude; interpretation reviewed and agreed by me |

### Use of AI

I used Claude, an AI assistant made by Anthropic, while working on the course tutorials and to
build this repository. I decided what to include, reviewed every result and interpretation, and the findings follow my answers to
the course questions.

## Reproducing the results

The course model and data are not mine to share, so they are not in this repository. With access
to the course folder:

```bash
conda activate <your environment>   # pandas, numpy, scipy, matplotlib, openpyxl
export CE48V_COURSE_DIR=/path/to/course/tutorials
cd analysis
python 01_inflow_vs_demand.py
python 02_drought_storage.py
python 03_pareto_front.py
python 04_climate_scenarios.py
python 05_robustness.py
```

Figures go to `figures/` and tables to `results/`. `03_pareto_front.py` reads the saved NSGA-II
front instead of re-running the optimisation, because NSGA-II is stochastic and a new run would
shift every number.

## Acknowledgements

This work was done in CE48V, Water Resources Systems Analysis and Intelligent Decision Support,
taught by Dr. Veysel Yıldız at Boğaziçi University in Fall 2026. The reservoir model, the tutorials,
the inflow data and the flow duration curve model were provided as course material. They are not
included here and belong to the course.

## References

- Deb, K., Pratap, A., Agarwal, S. and Meyarivan, T. (2002), A fast and elitist multiobjective
  genetic algorithm: NSGA-II, *IEEE Transactions on Evolutionary Computation*, 6(2), 182-197.
- Hashimoto, T., Stedinger, J. R. and Loucks, D. P. (1982), Reliability, resiliency, and
  vulnerability criteria for water resource system performance evaluation, *Water Resources
  Research*, 18(1), 14-20.
- Rhodium, the open-source library for robust decision making used in the course optimisation
  set-up, Project Platypus: https://github.com/Project-Platypus/Rhodium
- Zatarain Salazar et al. (2016), source of the Conowingo system description used in the course.
- Yildiz et al. (2023), *Hydrology and Earth System Sciences*, 27, 2499, the flow duration curve
  model behind the Amplified Extremes scenarios: https://hess.copernicus.org/articles/27/2499/2023/
