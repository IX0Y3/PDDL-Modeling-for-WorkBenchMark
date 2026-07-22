"""Load WorkBenchMark YAML task specs into typed structures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

# (x, y, z) position or (roll, pitch, yaw) rotation from the YAML.
Vec3 = tuple[float, float, float]


# One brick as written in the YAML (name, type, color, pose).
@dataclass(frozen=True)
class BrickSpec:
    name: str
    type: str
    color: str
    pos: Vec3
    rotation: Vec3


# Full task: goal assembly + where bricks start in the pick area.
@dataclass(frozen=True)
class TaskSpec:
    goal_blocks: tuple[BrickSpec, ...]
    initial_blocks: tuple[BrickSpec, ...]
    source: Path | None = None

    # Convenient list of goal brick names, in YAML order.
    @property
    def brick_names(self) -> tuple[str, ...]:
        return tuple(b.name for b in self.goal_blocks)


# Entry point: read a ground_truth YAML file from disk → TaskSpec.
def load_task(path: str | Path) -> TaskSpec:
    # Convert path to Path object.
    path = Path(path)
    # Open the file and load the YAML.
    with path.open(encoding="utf-8") as f:
        # Load the YAML into a Python object.
        raw = yaml.safe_load(f)
    # Build the TaskSpec object.
    return task_from_mapping(raw, source=path)


# Same as load_task, but input is already a Python object (e.g. from tests).
def task_from_mapping(
    raw: Any,
    *,
    source: Path | None = None,
) -> TaskSpec:

    # Validate that YAML root is a mapping.
    if not isinstance(raw, Mapping):
        raise ValueError("task YAML root must be a mapping")

    # goal -> "blocks" = target assembly
    goal = _parse_brick_list(raw.get("blocks"), field="blocks")
    # initial -> "initial_blocks" = pick-area layout
    initial = _parse_brick_list(raw.get("initial_blocks"), field="initial_blocks")

    # Validate name coverage between goal and initial.
    # Every goal brick must appear in the initial list by name, and names must be unique.
    _validate_name_coverage(goal, initial)

    # Return the TaskSpec object.
    return TaskSpec(
        goal_blocks=tuple(goal),
        initial_blocks=tuple(initial),
        source=source,
    )


# Turn a YAML list under `blocks` / `initial_blocks` into BrickSpec objects.
def _parse_brick_list(value: Any, *, field: str) -> list[BrickSpec]:
    # Validate that the value is a list and is not empty.
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field!r} must be a non-empty list")
    # Parse each brick in the list.
    bricks: list[BrickSpec] = []
    for index, item in enumerate(value):
        # Parse the brick.
        brick = _parse_brick(item, field=field, index=index)
        # Add the brick to the list.
        bricks.append(brick)
    # Return the list of bricks.
    return bricks


# Parse a single brick dict; `field`/`index` only improve error messages.
def _parse_brick(item: Any, *, field: str, index: int) -> BrickSpec:
    
    # Construct the error message so we can reuse it
    where = f"{field}[{index}]"

    # Validate that the item is a mapping.
    if not isinstance(item, Mapping):
        raise ValueError(f"{where} must be a mapping")

    # Extract the brick properties.
    try:
        name = str(item["name"])
        brick_type = str(item["type"])
        color = str(item["color"])
        pos = _parse_vec3(item["pos"], field=f"{where}.pos")
        rotation = _parse_vec3(item["rotation"], field=f"{where}.rotation")

    # If the item is not a mapping, raise a ValueError.
    except KeyError as exc:
        raise ValueError(f"{where} missing required key {exc.args[0]!r}") from exc

    # Validate that the name is non-empty.
    if not name:
        raise ValueError(f"{where}.name must be non-empty")

    # Validate that the type is non-empty.
    if not brick_type:
        raise ValueError(f"{where}.type must be non-empty")

    # Return the BrickSpec object.
    return BrickSpec(
        name=name,
        type=brick_type,
        color=color,
        pos=pos,
        rotation=rotation,
    )


# YAML pos/rotation must be exactly three numbers → float triple.
def _parse_vec3(value: Any, *, field: str) -> Vec3:
    # Validate that the value is a sequence of 3 numbers.
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{field} must be a sequence of 3 numbers")
    if len(value) != 3:
        raise ValueError(f"{field} must have length 3, got {len(value)}")

    # Check that it only contains numbers.
    if not all(isinstance(v, (int, float)) for v in value):
        raise ValueError(f"{field} must contain only numbers")

    # Convert the value to a float triple.
    return (float(value[0]), float(value[1]), float(value[2]))


# Goal bricks must exist in the pick area
# Names must be unique in each list.
def _validate_name_coverage(
    goal: Sequence[BrickSpec],
    initial: Sequence[BrickSpec],
) -> None:
    # Extract the names of the initial bricks.
    initial_names = {b.name for b in initial}

    # Find the names of the goal bricks that are not in the initial bricks.
    missing = [b.name for b in goal if b.name not in initial_names]

    # If there are missing bricks, raise a ValueError.
    if missing:
        raise ValueError(
            "goal bricks missing from initial_blocks: " + ", ".join(missing)
        )

    # Validate that the names are unique in the goal bricks.
    goal_names = [b.name for b in goal]
    if len(goal_names) != len(set(goal_names)):
        raise ValueError("duplicate brick names in blocks")

    # Validate that the names are unique in the initial bricks.
    initial_name_list = [b.name for b in initial]
    if len(initial_name_list) != len(set(initial_name_list)):
        raise ValueError("duplicate brick names in initial_blocks")
