"""Smoke tests: the environment and imports are ready for Project P1."""

import importlib

import pytest


@pytest.mark.parametrize("module", ["tampanda", "unified_planning", "yaml", "numpy"])
def test_core_dependency_importable(module):
    importlib.import_module(module)


def test_workbenchmark_pddl_package_importable():
    import workbenchmark_pddl

    assert workbenchmark_pddl.__version__


def test_pyperplan_planner_available():
    import unified_planning.shortcuts as up

    up.get_environment().credits_stream = None
    with up.OneshotPlanner(name="pyperplan") as planner:
        assert planner is not None
