from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import cv2
import gymnasium
import stable_baselines3
import torch

from facade_uav.rl.gym_env import FacadeGymEnv


env = FacadeGymEnv()
obs, _ = env.reset()
print(
    {
        "cv2": cv2.__version__,
        "gymnasium": gymnasium.__version__,
        "stable_baselines3": stable_baselines3.__version__,
        "torch": torch.__version__,
        "observation_shape": tuple(obs.shape),
    }
)
