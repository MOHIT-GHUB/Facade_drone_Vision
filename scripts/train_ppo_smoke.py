from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.rl.ppo_trainer import train_ppo


if __name__ == "__main__":
    train_ppo(1500, str(ROOT / "outputs" / "rl" / "ppo_facade_policy"))
