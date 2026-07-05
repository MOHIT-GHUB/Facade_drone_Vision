from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.rl.coverage_env import FacadeCoverageEnv, lawnmower_policy


def main() -> None:
    env = FacadeCoverageEnv(width=12, height=8, seed=11)
    env.reset()
    total_reward = 0.0
    done = False
    steps = 0
    for action in lawnmower_policy(env):
        _, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1
        if done:
            break
    print(
        {
            "policy": "lawnmower",
            "steps": steps,
            "done": done,
            "total_reward": round(total_reward, 3),
            "coverage_ratio": round(float(info["coverage_ratio"]), 3),
            "last_safety": info["safety"],
        }
    )


if __name__ == "__main__":
    main()
