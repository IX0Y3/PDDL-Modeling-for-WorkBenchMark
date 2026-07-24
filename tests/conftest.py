"""
Shared pytest configuration for Project P1 tests.

It contains helper functions and fixtures for the Project P1 tests:

- Helper function to get the path to a ground truth task.
- Fixture to get the path to a ground truth task.
"""

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"

# Allow tests to import the package from source even without an editable install.
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Sibling clone: /work/rleap1/aifr/prak4/dataset (see README).
DATASET_ROOT = Path(__file__).resolve().parents[2] / "dataset"
GROUND_TRUTH_ROOT = DATASET_ROOT / "ground_truth"


# Helper function to get the path to a ground truth task.
def ground_truth_task(tier: int, task_id: int) -> Path:
    # Construct the path to the task.
    path = GROUND_TRUTH_ROOT / f"tier{tier}" / f"task_{task_id:03d}.yaml"
    # Validate that the task file exists.
    if not path.is_file():
        pytest.skip(f"WorkBenchMark dataset task not found: {path}")
    return path


# Fixture to get the path to a tier 1 task.
# Should return the path to the task.
@pytest.fixture
def tier1_task_001() -> Path:
    # Return the path to the task.
    return ground_truth_task(tier=1, task_id=1)


# Fixture to get the path to a tier 2 task.
# Should return the path to the task.
@pytest.fixture
def tier2_task_001() -> Path:
    # Return the path to the task.
    return ground_truth_task(tier=2, task_id=1)


# Fixture to get the path to a tier 3 task.
# Should return the path to the task.
@pytest.fixture
def tier3_task_001() -> Path:
    # Return the path to the task.
    return ground_truth_task(tier=3, task_id=1)
