from pathlib import Path

import pandas as pd

from backend.services.ais_analysis.validator import AISValidator


# Anchor for dataset paths so the loader works no matter which directory the
# backend is started from. loader.py -> ais_analysis -> services -> backend -> root.
REPO_ROOT = Path(__file__).resolve().parents[3]


class AISLoader:

    def __init__(self, csv_path=None):

        if csv_path is None:
            # Check runtime config first, then fall back to default
            try:
                from backend.api.config_store import get_config
                csv_path = get_config().get("ais_csv_path", str(REPO_ROOT / "dataset/raw/ais_data/ais_data.csv"))
                if not Path(csv_path).is_absolute():
                    csv_path = REPO_ROOT / csv_path
            except Exception:
                csv_path = REPO_ROOT / "dataset/raw/ais_data/ais_data.csv"

        self.csv_path = Path(csv_path)

        self.data = None

    def load(self):

        self.data = pd.read_csv(self.csv_path)

        AISValidator.validate(self.data)

        return self.data