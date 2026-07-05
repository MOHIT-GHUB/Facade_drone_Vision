from dataclasses import dataclass


@dataclass(frozen=True)
class VelocityCommand:
    vx_mps: float
    vy_mps: float
    vz_mps: float
    yaw_rate_rps: float = 0.0


def clamp_velocity(command: VelocityCommand, max_speed_mps: float = 0.8) -> VelocityCommand:
    def clamp(value: float) -> float:
        return max(-max_speed_mps, min(max_speed_mps, value))

    return VelocityCommand(
        vx_mps=clamp(command.vx_mps),
        vy_mps=clamp(command.vy_mps),
        vz_mps=clamp(command.vz_mps),
        yaw_rate_rps=max(-0.5, min(0.5, command.yaw_rate_rps)),
    )
