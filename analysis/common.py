"""Shared helpers: locate the course model, load the Conowingo system, save figures."""
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
FIGURES = REPO / "figures"
RESULTS = REPO / "results"

RESERVOIR = "Conowingo"
DOWNSTREAM = ["Environmental"]
ON_SITE = ["Baltimore", "Chester", "Nuclear plant"]

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
})


def course_dir() -> Path:
    """Folder that holds the course `model/` package and `data/Conowingo_data.xlsx`."""
    value = os.environ.get("CE48V_COURSE_DIR")
    if not value:
        sys.exit("Set CE48V_COURSE_DIR to the course tutorials folder. See README, 'Reproducing the results'.")
    path = Path(value).resolve()
    if not (path / "model").is_dir() or not (path / "data").is_dir():
        sys.exit(f"{path} does not contain the course model/ and data/ folders.")
    return path


def load_system():
    """Return the course model modules, the Conowingo reservoir object and the raw flow table."""
    path = course_dir()
    os.chdir(path)  # the course model reads data/ with a relative path
    sys.path.insert(0, str(path))
    from model import setup, balance_calcs, performance

    reservoir = setup.define_reservoir(RESERVOIR, DOWNSTREAM, ON_SITE)
    flows = setup.extract_flows(reservoir=reservoir)
    return setup, balance_calcs, performance, reservoir, flows


def save(fig, name: str):
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / name)
    plt.close(fig)
    print(f"saved figures/{name}")
