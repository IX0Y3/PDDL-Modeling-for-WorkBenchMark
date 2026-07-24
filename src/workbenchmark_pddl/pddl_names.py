"""PDDL object-name helpers and shared problem constants."""

from __future__ import annotations

from workbenchmark_pddl.task import TaskSpec

# Name of the used PDDL domain
DOMAIN_NAME = "lego-assembly"

# End-effector object name
GRIPPER_NAME = "gripper"

# Pick area object name
PICK_AREA = "pick_area"

# Assembly area object name
ASSEMBLY_AREA = "assembly_area"


# PDDL tokens must not start with a digit (YAML has names like 4x2_brick_1).
def brick_object(name: str) -> str:
    return f"b_{_sanitize(name)}"


# Brick type object name (type_4x2 instead of brick_4x2)
def type_object(brick_type: str) -> str:
    return "type_" + brick_type.removeprefix("brick_")

# Stud object name (stud_x_y)
def stud_object(sx: int, sy: int) -> str:
    return f"stud_{_coord(sx)}_{_coord(sy)}"

# Layer object name (layer_1, layer_2, ...)
def layer_object(layer: int) -> str:
    return f"layer_{layer}"


# Rotation object name (rot_0, rot_90, ...)
def rot_object(rot: int) -> str:
    return f"rot_{rot}"


# Private function to convert negative stud indices to m1, m2, (m = minus / no - in PDDL names).
def _coord(value: int) -> str:
    return f"m{-value}" if value < 0 else str(value)


# Private function to sanitize token (replace "-" with "_")
def _sanitize(token: str) -> str:
    return token.replace("-", "_")


# Default problem name (lego_task or the name of the source file)
def default_problem_name(task: TaskSpec) -> str:
    if task.source is not None:
        return _sanitize(task.source.stem)
    return "lego_task"
