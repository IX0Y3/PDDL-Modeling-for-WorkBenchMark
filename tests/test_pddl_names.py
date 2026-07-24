"""Tests for PDDL object-name helpers."""

from workbenchmark_pddl.pddl_names import (
    brick_object,
    default_problem_name,
    layer_object,
    rot_object,
    stud_object,
    type_object,
)
from workbenchmark_pddl.task import TaskSpec


# Test the brick object prefixes leading digits.
# Should prefix with "b_" and encode leading digits.
def test_brick_object_prefixes_leading_digits():
    # Check the brick object prefixes leading digits.
    assert brick_object("4x2_brick_1") == "b_4x2_brick_1"
    assert brick_object("2x2_brick_2") == "b_2x2_brick_2"


# Test the type object strips brick prefix.
# Should remove "brick_" prefix and encode type name.
def test_type_object_strips_brick_prefix():
    # Check the type object strips brick prefix.
    assert type_object("brick_4x2") == "type_4x2"
    assert type_object("brick_2x2") == "type_2x2"


# Test the stud object encodes negative coordinates.
# Should prefix with "stud_" and encode negative coordinates.
def test_stud_object_encodes_negative_coords():
    # Check the stud object encodes negative coordinates.
    assert stud_object(0, 9) == "stud_0_9"
    assert stud_object(-1, 7) == "stud_m1_7"
    assert stud_object(-3, -2) == "stud_m3_m2"


# Test the layer and rot objects encode layer and rotation numbers.
# Should prefix with "layer_" or "rot_" and encode layer/rotation numbers.
def test_layer_and_rot_objects():
    # Check the layer and rot objects encode layer and rotation numbers.
    assert layer_object(0) == "layer_0"
    assert layer_object(2) == "layer_2"
    assert rot_object(0) == "rot_0"
    assert rot_object(90) == "rot_90"


# Test the default problem name without source.
# Should return "lego_task" for empty task.
def test_default_problem_name_without_source():
    # Check the default problem name without source.
    task = TaskSpec(goal_blocks=(), initial_blocks=())
    assert default_problem_name(task) == "lego_task"
