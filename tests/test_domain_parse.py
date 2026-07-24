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

EXPECTED_TYPES = {
    "brick",
    "brick-type",
    "endeffector",
    "stud",
    "layer",
    "rot",
    "area",
}
EXPECTED_PREDICATES = {
    "at-stud",
    "at-layer",
    "oriented",
    "in-area",
    "clear",
    "supports",
    "holding",
    "gripper-empty",
    "occupied",
    "free",
    "is-type",
    "area-pick",
    "area-assembly",
    "base-layer",
    "above",
    "footprint",
    "can-attach",
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


def test_stack_mentions_can_attach(parsed_domain):
    """Half-overlap / rotation validity must be a stack precondition."""
    stack = next(a for a in parsed_domain.actions if a.name == "stack")
    pre_names = {str(p) for p in stack.preconditions}
    assert any("can-attach" in name for name in pre_names)
