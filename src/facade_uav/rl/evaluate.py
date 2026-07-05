from __future__ import annotations

from pathlib import Path

from facade_uav.rl.coverage_env import (
    FacadeCoverageEnv,
    greedy_nearest_dirty_action,
    lawnmower_policy,
)


def evaluate_lawnmower(seed: int = 11) -> dict[str, object]:
    env = FacadeCoverageEnv(width=12, height=8, seed=seed)
    env.reset()
    total_reward = 0.0
    done = False
    info: dict[str, object] = {"coverage_ratio": 0.0, "safety": "not_started"}
    steps = 0
    for action in lawnmower_policy(env):
        _, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1
        if done:
            break
    return {
        "policy": "lawnmower",
        "seed": seed,
        "steps": steps,
        "done": done,
        "total_reward": round(total_reward, 3),
        "coverage_ratio": round(float(info["coverage_ratio"]), 3),
        "last_safety": info["safety"],
    }


def evaluate_greedy(seed: int = 11, max_steps: int = 288) -> dict[str, object]:
    env = FacadeCoverageEnv(width=12, height=8, seed=seed)
    env.reset()
    total_reward = 0.0
    done = False
    info: dict[str, object] = {"coverage_ratio": 0.0, "safety": "not_started"}
    steps = 0
    while not done and steps < max_steps:
        _, reward, done, info = env.step(greedy_nearest_dirty_action(env))
        total_reward += reward
        steps += 1
    return {
        "policy": "greedy_nearest_dirty",
        "seed": seed,
        "steps": steps,
        "done": done,
        "total_reward": round(total_reward, 3),
        "coverage_ratio": round(float(info["coverage_ratio"]), 3),
        "last_safety": info["safety"],
    }


def evaluate_ppo(model_path: str | Path, seed: int = 11, max_steps: int = 288) -> dict[str, object]:
    try:
        from stable_baselines3 import PPO
    except ModuleNotFoundError as exc:
        raise RuntimeError("Stable-Baselines3 is required for PPO evaluation.") from exc

    from facade_uav.rl.gym_env import FacadeGymEnv

    env = FacadeGymEnv(width=12, height=8, seed=seed)
    model = PPO.load(str(model_path))
    obs, _ = env.reset(seed=seed)
    total_reward = 0.0
    info: dict[str, object] = {"coverage_ratio": 0.0, "safety": "not_started"}
    terminated = False
    truncated = False
    steps = 0
    while not (terminated or truncated) and steps < max_steps:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        steps += 1
    return {
        "policy": "ppo",
        "seed": seed,
        "steps": steps,
        "done": bool(terminated or truncated),
        "total_reward": round(total_reward, 3),
        "coverage_ratio": round(float(info["coverage_ratio"]), 3),
        "last_safety": info["safety"],
    }
