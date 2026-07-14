"""Tests for the LEGO assembly PDDL domain."""

from pathlib import Path

import pytest
from unified_planning.io import PDDLReader

DOMAIN_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "workbenchmark_pddl"
    / "pddl"
    / "lego_domain.pddl"
)

EXPECTED_TYPES = {"brick", "gripper", "area", "grid_loc"}
EXPECTED_PREDICATES = {
    "stacked-on",
    "on-table",
    "clear",
    "graspable",
    "in-pick-area",
    "in-asm-area",
    "target-pose",
    "holding",
    "gripper-empty",
}
EXPECTED_ACTIONS = {"pick", "place", "stack"}


@pytest.fixture(scope="module")
def parsed_domain():
    assert DOMAIN_PATH.is_file(), f"domain file missing: {DOMAIN_PATH}"
    return PDDLReader().parse_problem(str(DOMAIN_PATH))


def test_domain_file_exists():
    assert DOMAIN_PATH.is_file()


def test_domain_name(parsed_domain):
    assert parsed_domain.name == "lego-assembly"


def test_domain_types(parsed_domain):
    assert {t.name for t in parsed_domain.user_types} == EXPECTED_TYPES


def test_domain_predicates(parsed_domain):
    assert {f.name for f in parsed_domain.fluents} == EXPECTED_PREDICATES


def test_domain_actions(parsed_domain):
    assert {a.name for a in parsed_domain.actions} == EXPECTED_ACTIONS
