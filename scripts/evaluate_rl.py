from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.rl.evaluate import evaluate_greedy, evaluate_lawnmower, evaluate_ppo


def main() -> None:
    output_dir = ROOT / "outputs" / "rl"
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "ppo_facade_policy.zip"
    results = [evaluate_lawnmower(seed=11), evaluate_greedy(seed=11)]
    if model_path.exists():
        results.append(evaluate_ppo(model_path, seed=11))
    else:
        results.append({"policy": "ppo", "status": "missing_model", "expected": str(model_path)})
    out = output_dir / "evaluation.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
