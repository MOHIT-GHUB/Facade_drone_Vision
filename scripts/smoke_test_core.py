from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.cleaning_zone_map import CleaningZoneMap
from facade_uav.config import MissionState, SafetyBounds
from facade_uav.planning.coverage_path import find_grid_route, plan_obstacle_aware_cleaning_route
from facade_uav.rl.coverage_env import FacadeCoverageEnv
from facade_uav.safety_layer import SafetyLayer


def test_zone_map() -> None:
    zone_map = CleaningZoneMap(width=4, height=3, default_depth_m=1.5)
    zone_map.set_dirty(1, 1, 0.9)
    zone_map.mark_cleaned(1, 1)
    assert zone_map.coverage_ratio() == 1.0 / 12.0
    assert zone_map.dirty_cells() == []
    zone_map.mark_object(2, 1, "balcony", 0.9, "blocked")
    assert zone_map.object_summary()["balcony"] == 1


def test_object_aware_route() -> None:
    zone_map = CleaningZoneMap(width=5, height=5)
    for z in range(4):
        zone_map.mark_object(2, z, "ledge", 0.9, "blocked")
    zone_map.set_dirty(4, 4, 0.9)
    route = find_grid_route(zone_map, (0, 0), (4, 4), clearance_cells=0)
    assert route
    assert (2, 0) not in route
    plan = plan_obstacle_aware_cleaning_route(zone_map, start=(0, 0), threshold=0.25, clearance_cells=0)
    assert plan["steps"][-1]["action"] == "clean"


def test_safety_layer() -> None:
    bounds = SafetyBounds()
    layer = SafetyLayer(bounds)
    state = MissionState(
        x_m=0.0,
        y_m=0.0,
        z_m=2.0,
        standoff_m=0.5,
        wind_mps=1.0,
        reservoir_l=2.0,
        battery_pct=80.0,
    )
    decision = layer.evaluate(state, proposed_command={"vx": 0.4})
    assert not decision.allowed
    assert decision.action == "hold"
    assert "standoff" in decision.reason


def test_coverage_env() -> None:
    env = FacadeCoverageEnv(width=5, height=4, seed=7)
    obs = env.reset()
    assert obs["coverage_ratio"] == 0.0
    for _ in range(5):
        obs, reward, done, info = env.step((1, 0))
        assert "reward_terms" in info
        if done:
            break
    assert obs["reservoir_l"] < 5.0


if __name__ == "__main__":
    test_zone_map()
    test_object_aware_route()
    test_safety_layer()
    test_coverage_env()
    print("core smoke test passed")
