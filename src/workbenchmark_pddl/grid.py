"""Quantize continuous WorkBenchMark poses onto the Duplo stud grid."""

from __future__ import annotations

from dataclasses import dataclass

from workbenchmark_pddl.task import BrickSpec, Vec3

# Duplo stud spacing and brick height (metres), matching the dataset.
# Extracted from the dataset.
STUD_PITCH_M = 0.016
LAYER_HEIGHT_M = 0.0191


# Discrete pose used by the PDDL domain: grid cell + layer + yaw.
@dataclass(frozen=True)
class DiscretePose:
    # X coordinate of the stud
    stud_x: int
    # Y coordinate of the stud
    stud_y: int
    # Layer of the brick
    layer: int
    # Rotation of the brick in degrees, only 0 or 90 for our brick types
    rot: int


# Map continuous (pos, rotation) → DiscretePose.
def quantize_pose(
    pos: Vec3,
    rotation: Vec3,
    *,
    z_origin: float = 0.0,
) -> DiscretePose:
    # Get the x, y, z coordinates of the brick
    x, y, z = pos

    # Quantize the x, y, z coordinates to the nearest stud, layer, and rotation
    stud_x = _quantize_axis(x, STUD_PITCH_M)
    stud_y = _quantize_axis(y, STUD_PITCH_M)
    layer = _quantize_axis(z - z_origin, LAYER_HEIGHT_M)
    rot = quantize_yaw(rotation[2])

    # Return the discrete pose
    return DiscretePose(stud_x=stud_x, stud_y=stud_y, layer=layer, rot=rot)


# Convenience wrapper for a BrickSpec (same defaults as quantize_pose).
def quantize_brick(brick: BrickSpec, *, z_origin: float = 0.0) -> DiscretePose:
    return quantize_pose(brick.pos, brick.rotation, z_origin=z_origin)


# Yaw = rotation around the vertical axis (top-down).
# Dataset only uses 0/90; 180/270 fold to the same footprints for 2x2/4x2.
def quantize_yaw(yaw_deg: float) -> int:
    quarter = int(round(float(yaw_deg) / 90.0)) % 4
    return 0 if quarter % 2 == 0 else 90


# Private function to round a metre value to the nearest integer grid step.
def _quantize_axis(value_m: float, step_m: float) -> int:
    return int(round(float(value_m) / step_m))
