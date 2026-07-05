from dataclasses import dataclass


@dataclass
class PanelCell:
    dirty_confidence: float = 0.0
    obstacle: bool = False
    surface_type: str = "glass"
    object_type: str = "none"
    object_confidence: float = 0.0
    risk_level: str = "clear"
    depth_m: float = 1.5
    thermal_anomaly: bool = False
    cleaned: bool = False

    @property
    def cleanable(self) -> bool:
        return self.surface_type == "glass" and not self.obstacle


class CleaningZoneMap:
    """Grid representation of facade cleaning state.

    This is intentionally dependency-free so the safety and RL logic can be
    tested before OpenCV or ROS 2 are installed.
    """

    def __init__(self, width: int, height: int, default_depth_m: float = 1.5) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        self.width = width
        self.height = height
        self.cells = [
            [PanelCell(depth_m=default_depth_m) for _ in range(width)]
            for _ in range(height)
        ]

    def in_bounds(self, x: int, z: int) -> bool:
        return 0 <= x < self.width and 0 <= z < self.height

    def cell(self, x: int, z: int) -> PanelCell:
        if not self.in_bounds(x, z):
            raise IndexError(f"cell out of bounds: {(x, z)}")
        return self.cells[z][x]

    def set_dirty(self, x: int, z: int, confidence: float) -> None:
        self.cell(x, z).dirty_confidence = max(0.0, min(1.0, confidence))

    def set_obstacle(self, x: int, z: int, obstacle: bool = True) -> None:
        self.cell(x, z).obstacle = obstacle
        if obstacle:
            self.cell(x, z).surface_type = "frame"
            if self.cell(x, z).object_type == "none":
                self.mark_object(x, z, "frame", 1.0, "blocked")

    def set_surface_type(self, x: int, z: int, surface_type: str) -> None:
        allowed = {"glass", "concrete", "frame", "unknown"}
        if surface_type not in allowed:
            raise ValueError(f"surface_type must be one of {sorted(allowed)}")
        cell = self.cell(x, z)
        cell.surface_type = surface_type
        cell.obstacle = surface_type == "frame"
        if surface_type == "frame":
            self.mark_object(x, z, "frame", max(cell.object_confidence, 0.8), "blocked")

    def set_depth(self, x: int, z: int, depth_m: float) -> None:
        if depth_m <= 0.0:
            raise ValueError("depth_m must be positive")
        self.cell(x, z).depth_m = depth_m

    def set_thermal_anomaly(self, x: int, z: int, anomaly: bool = True) -> None:
        self.cell(x, z).thermal_anomaly = anomaly
        if anomaly:
            self.mark_object(x, z, "thermal_anomaly", 1.0, "caution")

    def mark_object(
        self,
        x: int,
        z: int,
        object_type: str,
        confidence: float = 1.0,
        risk_level: str = "blocked",
    ) -> None:
        allowed_risk = {"clear", "caution", "blocked"}
        if risk_level not in allowed_risk:
            raise ValueError(f"risk_level must be one of {sorted(allowed_risk)}")
        cell = self.cell(x, z)
        cell.object_type = object_type
        cell.object_confidence = max(0.0, min(1.0, confidence))
        cell.risk_level = risk_level
        if risk_level == "blocked":
            cell.obstacle = True
            cell.surface_type = "frame"
            cell.dirty_confidence = 0.0

    def blocked_cells(self, clearance_cells: int = 0) -> set[tuple[int, int]]:
        """Return obstacle cells inflated by a grid-cell clearance radius."""

        blocked: set[tuple[int, int]] = set()
        for z in range(self.height):
            for x in range(self.width):
                cell = self.cells[z][x]
                if not cell.obstacle and cell.risk_level != "blocked":
                    continue
                for dz in range(-clearance_cells, clearance_cells + 1):
                    for dx in range(-clearance_cells, clearance_cells + 1):
                        bx, bz = x + dx, z + dz
                        if self.in_bounds(bx, bz):
                            blocked.add((bx, bz))
        return blocked

    def mark_cleaned(self, x: int, z: int) -> bool:
        target = self.cell(x, z)
        if not target.cleanable:
            return False
        was_new = not target.cleaned and target.dirty_confidence > 0.0
        target.cleaned = True
        target.dirty_confidence = 0.0
        return was_new

    def dirty_cells(self, threshold: float = 0.5) -> list[tuple[int, int]]:
        cells: list[tuple[int, int]] = []
        for z in range(self.height):
            for x in range(self.width):
                cell = self.cells[z][x]
                if cell.cleanable and not cell.cleaned and cell.dirty_confidence >= threshold:
                    cells.append((x, z))
        return cells

    def coverage_ratio(self) -> float:
        cleanable = 0
        cleaned = 0
        for row in self.cells:
            for cell in row:
                if not cell.cleanable:
                    continue
                cleanable += 1
                if cell.cleaned:
                    cleaned += 1
        if cleanable == 0:
            return 1.0
        return cleaned / cleanable

    def summary(self) -> dict[str, float]:
        obstacle_count = 0
        thermal_count = 0
        dirty_count = 0
        cleanable_count = 0
        concrete_count = 0
        frame_count = 0
        unknown_count = 0
        caution_count = 0
        for row in self.cells:
            for cell in row:
                obstacle_count += int(cell.obstacle)
                thermal_count += int(cell.thermal_anomaly)
                cleanable_count += int(cell.cleanable)
                concrete_count += int(cell.surface_type == "concrete")
                frame_count += int(cell.surface_type == "frame")
                unknown_count += int(cell.surface_type == "unknown")
                caution_count += int(cell.risk_level == "caution")
                dirty_count += int(
                    cell.cleanable and not cell.cleaned and cell.dirty_confidence >= 0.25
                )
        return {
            "width": float(self.width),
            "height": float(self.height),
            "coverage_ratio": self.coverage_ratio(),
            "dirty_count": float(dirty_count),
            "cleanable_glass_count": float(cleanable_count),
            "concrete_count": float(concrete_count),
            "frame_count": float(frame_count),
            "unknown_count": float(unknown_count),
            "obstacle_count": float(obstacle_count),
            "caution_count": float(caution_count),
            "thermal_anomaly_count": float(thermal_count),
        }

    def object_summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in self.cells:
            for cell in row:
                if cell.object_type == "none":
                    continue
                counts[cell.object_type] = counts.get(cell.object_type, 0) + 1
        return counts

    def to_plan_targets(self, threshold: float = 0.25) -> list[dict[str, float | int | str]]:
        targets: list[dict[str, float | int | str]] = []
        for x, z in self.dirty_cells(threshold=threshold):
            cell = self.cell(x, z)
            targets.append(
                {
                    "x": x,
                    "z": z,
                    "surface_type": cell.surface_type,
                    "dirty_confidence": round(cell.dirty_confidence, 3),
                    "depth_m": round(cell.depth_m, 3),
                    "risk_level": cell.risk_level,
                }
            )
        return targets
