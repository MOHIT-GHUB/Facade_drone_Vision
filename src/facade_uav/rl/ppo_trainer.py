from __future__ import annotations

import argparse
from pathlib import Path


def train_ppo(timesteps: int, output_path: str) -> None:
    try:
        from stable_baselines3 import PPO
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PPO training requires gymnasium and stable-baselines3. "
            "Install dependencies with: python -m pip install -r requirements.txt"
        ) from exc

    from facade_uav.rl.gym_env import FacadeGymEnv

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    env = FacadeGymEnv(width=12, height=8, seed=42)
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        n_steps=256,
        batch_size=64,
        gamma=0.98,
        learning_rate=3e-4,
        device="cpu",
    )
    model.learn(total_timesteps=timesteps)
    model.save(str(output))
    print(f"saved PPO model to {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=10000)
    parser.add_argument("--output", default="outputs/ppo_facade_policy")
    args = parser.parse_args()
    train_ppo(args.timesteps, args.output)


if __name__ == "__main__":
    main()
