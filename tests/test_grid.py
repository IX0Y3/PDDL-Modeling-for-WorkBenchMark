"""Tests for continuous pose → stud/layer/rot quantization."""

from pathlib import Path

import pytest

from workbenchmark_pddl.grid import (
    LAYER_HEIGHT_M,
    STUD_PITCH_M,
    DiscretePose,
    quantize_brick,
    quantize_pose,
    quantize_yaw,
)
from workbenchmark_pddl.task import load_task


# Test the quantize_yaw function
# Should fold 0, 90, 180, 270, and -90 to 0 or 90.
def test_quantize_yaw_folds_to_0_or_90():

    # 0 Maps to 0
    assert quantize_yaw(0) == 0
    # 90 Maps to 90
    assert quantize_yaw(90) == 90
    # 180 Maps to 0
    assert quantize_yaw(180) == 0
    # 270 Maps to 90
    assert quantize_yaw(270) == 90
    # -90 Maps to 90
    assert quantize_yaw(-90) == 90


# Test the quantize_pose function
# Should quantize a basic stack to the correct layer and rotation.
def test_quantize_pose_basic_stack():

    # Quantize the base and top bricks (continuous -> discrete)
    base = quantize_pose((0.0, 0.148, 0.0), (0.0, 0.0, 0.0))
    top = quantize_pose((0.0, 0.148, LAYER_HEIGHT_M), (0.0, 0.0, 0.0))

    # Check the quantized base poses are correct
    assert base == DiscretePose(
        stud_x=0,
        stud_y=round(0.148 / STUD_PITCH_M),
        layer=0,
        rot=0,
    )

    # Check the quantized top poses are correct
    assert top.stud_x == base.stud_x
    assert top.stud_y == base.stud_y
    assert top.layer == base.layer + 1

# Tets if tier 1 task goal layers are correct
# Should quantize the base and top bricks to the correct layer and rotation.
def test_tier1_goal_layers(tier1_task_001: Path):

    # Load the task
    task = load_task(tier1_task_001)

    # Quantize the base and top bricks (continuous -> discrete)
    base = quantize_brick(task.goal_blocks[0])
    top = quantize_brick(task.goal_blocks[1])

    # Check the quantized base and top poses are correct
    assert base.layer == 0
    assert top.layer == 1
    assert base.stud_x == top.stud_x
    assert base.stud_y == top.stud_y
    assert base.rot == 0
    assert top.rot == 0

# Test if tier 2 task goal includes yaw 90
# Should quantize the goal blocks to include yaw 90.
def test_tier2_goal_includes_yaw_90(tier2_task_001: Path):

    # Load the task
    task = load_task(tier2_task_001)

    # Quantize the goal blocks (continuous -> discrete)
    yaws = {quantize_brick(b).rot for b in task.goal_blocks}

    # Check the quantized goal blocks include yaw 90
    assert yaws == {0, 90}


# Test if pick area is flat with local z origin
# Should quantize the initial brick to the correct layer.
def test_pick_area_flat_with_local_z_origin(tier1_task_001: Path):

    # Initial bricks sit on the table (z≈0.0495); local origin → layer 0.
    task = load_task(tier1_task_001)

    # Quantize the initial brick (continuous -> discrete)
    brick = task.initial_blocks[0]
    pose = quantize_brick(brick, z_origin=brick.pos[2])

    # Check the quantized initial brick is in layer 0
    assert pose.layer == 0
