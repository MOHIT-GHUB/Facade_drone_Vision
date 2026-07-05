from __future__ import annotations

from collections import deque

from facade_uav.cleaning_zone_map import CleaningZoneMap


GridCell = tuple[int, int]


def _neighbors(cell: GridCell) -> tuple[GridCell, GridCell, GridCell, GridCell]:
    x, z = cell
    return ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1))


def find_grid_route(
    zone_map: CleaningZoneMap,
    start: GridCell,
    goal: GridCell,
    clearance_cells: int = 1,
) -> list[GridCell]:
    """Find a grid route that avoids blocked cells plus safety clearance.

    Breadth-first search is enough here because grid moves have equal cost and
    the map is small. The goal cell itself is allowed because cleaning targets
    are cleanable cells adjacent to, but not inside, obstacles.
    """

    if not zone_map.in_bounds(*start):
        raise ValueError(f"start is out of bounds: {start}")
    if not zone_map.in_bounds(*goal):
        raise ValueError(f"goal is out of bounds: {goal}")

    blocked = zone_map.blocked_cells(clearance_cells=clearance_cells)
    blocked.discard(start)
    blocked.discard(goal)
    queue: deque[GridCell] = deque([start])
    previous: dict[GridCell, GridCell | None] = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for nxt in _neighbors(current):
            if not zone_map.in_bounds(*nxt) or nxt in blocked or nxt in previous:
                continue
            previous[nxt] = current
            queue.append(nxt)

    if goal not in previous:
        return []

    route = [goal]
    while route[-1] != start:
        parent = previous[route[-1]]
        if parent is None:
            break
        route.append(parent)
    route.reverse()
    return route


def plan_obstacle_aware_cleaning_route(
    zone_map: CleaningZoneMap,
    start: GridCell = (0, 0),
    threshold: float = 0.25,
    clearance_cells: int = 1,
) -> dict[str, object]:
    """Plan a route that identifies targets and detours around obstacles."""

    current = start
    remaining = set(zone_map.dirty_cells(threshold=threshold))
    route_steps: list[dict[str, float | int | str]] = []
    skipped_targets: list[dict[str, int | str]] = []

    while remaining:
        candidates: list[tuple[int, int, GridCell, list[GridCell]]] = []
        unreachable: list[GridCell] = []
        for target in sorted(remaining):
            route = find_grid_route(
                zone_map,
                current,
                target,
                clearance_cells=clearance_cells,
            )
            if not route:
                unreachable.append(target)
                continue
            candidates.append((len(route), abs(target[0] - current[0]) + abs(target[1] - current[1]), target, route))

        if not candidates:
            for target in sorted(unreachable):
                skipped_targets.append({"x": target[0], "z": target[1], "reason": "unreachable_with_clearance"})
            break

        _, _, target, route = min(candidates, key=lambda item: (item[0], item[1], item[2]))
        remaining.remove(target)
        for step in route[1:-1]:
            cell = zone_map.cell(*step)
            route_steps.append(
                {
                    "x": step[0],
                    "z": step[1],
                    "action": "transit",
                    "surface_type": cell.surface_type,
                    "risk_level": cell.risk_level,
                    "standoff_m": round(cell.depth_m, 3),
                }
            )
        target_cell = zone_map.cell(*target)
        route_steps.append(
            {
                "x": target[0],
                "z": target[1],
                "action": "clean",
                "surface_type": target_cell.surface_type,
                "dirty_confidence": round(target_cell.dirty_confidence, 3),
                "risk_level": target_cell.risk_level,
                "standoff_m": round(target_cell.depth_m, 3),
            }
        )
        current = target

    return {
        "policy": "obstacle_aware_bfs_clearance_route",
        "clearance_cells": clearance_cells,
        "start": {"x": start[0], "z": start[1]},
        "steps": route_steps,
        "skipped_targets": skipped_targets,
        "object_summary": zone_map.object_summary(),
        "zone_summary": zone_map.summary(),
    }


def plan_greedy_cleaning_path(
    zone_map: CleaningZoneMap,
    start: tuple[int, int] = (0, 0),
    threshold: float = 0.25,
) -> list[dict[str, float | int | str]]:
    """Return an ordered list of dirty cleanable-glass cells.

    This deliberately skips concrete, frames, unknown surfaces, and already
    cleaned cells. It is the trusted fallback until PPO passes its gate.
    """

    current_x, current_z = start
    remaining = set(zone_map.dirty_cells(threshold=threshold))
    path: list[dict[str, float | int | str]] = []

    while remaining:
        next_cell = min(
            remaining,
            key=lambda cell: abs(cell[0] - current_x) + abs(cell[1] - current_z),
        )
        remaining.remove(next_cell)
        current_x, current_z = next_cell
        cell = zone_map.cell(current_x, current_z)
        path.append(
            {
                "x": current_x,
                "z": current_z,
                "surface_type": cell.surface_type,
                "action": "clean",
                "dirty_confidence": round(cell.dirty_confidence, 3),
                "standoff_m": round(cell.depth_m, 3),
            }
        )

    return path
