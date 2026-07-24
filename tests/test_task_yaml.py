"""Tests for WorkBenchMark YAML → TaskSpec loading."""

from pathlib import Path

import pytest

from workbenchmark_pddl.task import BrickSpec, load_task, task_from_mapping

# Test loading a tier 1 task from the dataset.
# Should load the task from the dataset and validate the task.
def test_load_tier1_task_from_dataset(tier1_task_001: Path):
    # Load the task.
    task = load_task(tier1_task_001)

    # Validate the task.
    assert task.source == tier1_task_001

    # Validate the brick names.
    assert task.brick_names == ("4x2_brick_1", "4x2_brick_2")
    assert len(task.goal_blocks) == 2
    assert len(task.initial_blocks) == 2

    # Validate the first goal block.
    base = task.goal_blocks[0]
    assert base == BrickSpec(
        name="4x2_brick_1",
        type="brick_4x2",
        color="green",
        pos=(0.0, 0.148, 0.0),
        rotation=(0.0, 0.0, 0.0),
    )

    # Validate the second goal block.
    assert task.goal_blocks[1].pos[2] == pytest.approx(0.0191)


# Test rejecting a missing goal brick in the initial blocks list.
def test_rejects_missing_goal_brick_in_initial():
    # Construct the raw task.
    raw = {
        "blocks": [
            {
                "name": "a",
                "type": "brick_2x2",
                "color": "red",
                "pos": [0, 0, 0],
                "rotation": [0, 0, 0],
            }
        ],
        "initial_blocks": [
            {
                "name": "b",
                "type": "brick_2x2",
                "color": "red",
                "pos": [0.1, 0, 0],
                "rotation": [0, 0, 0],
            }
        ],
    }
    # Validate that the task is rejected.
    with pytest.raises(ValueError, match="missing from initial_blocks"):
        task_from_mapping(raw)


# Test rejecting a bad position length.
def test_rejects_bad_pos_length():
    # Construct the raw task.
    raw = {
        "blocks": [
            {
                "name": "a",
                "type": "brick_2x2",
                "color": "red",
                "pos": [0, 0],
                "rotation": [0, 0, 0],
            }
        ],
        "initial_blocks": [
            {
                "name": "a",
                "type": "brick_2x2",
                "color": "red",
                "pos": [0, 0, 0],
                "rotation": [0, 0, 0],
            }
        ],
    }
    # Validate that the task is rejected.
    with pytest.raises(ValueError, match="length 3"):
        task_from_mapping(raw)
