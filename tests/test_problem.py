"""Tests for YAML → PDDL problem generation."""

from pathlib import Path

import pytest
from unified_planning.io import PDDLReader

from workbenchmark_pddl.problem import domain_path, render_problem, write_problem
from workbenchmark_pddl.task import load_task


# Test the render_problem method parses with UPF.
# Should include domain, init, goal, and assembly area constraints.
@pytest.mark.parametrize(
    "fixture_name",
    ["tier1_task_001", "tier2_task_001", "tier3_task_001"],
)
def test_render_problem_parses_with_upf(fixture_name: str, request, tmp_path: Path):
    task_path: Path = request.getfixturevalue(fixture_name)
    task = load_task(task_path)
    problem_text = render_problem(task)

    assert "(:domain lego-assembly)" in problem_text
    assert "(:init" in problem_text
    assert "(:goal (and" in problem_text
    assert "(gripper-empty gripper)" in problem_text

    # Every goal brick must be asked for in the assembly area.
    for brick in task.goal_blocks:
        assert f"b_{brick.name}" in problem_text
        assert f"(in-area b_{brick.name} assembly_area)" in problem_text

    out = tmp_path / f"{task_path.stem}.pddl"
    write_problem(task, out)
    parsed = PDDLReader().parse_problem(str(domain_path()), str(out))
    assert parsed is not None
    assert len(parsed.actions) == 3

# Test the tier1 problem has stack geometry.
# Should include base-layer, above, can-attach, and footprint lines.
def test_tier1_problem_has_stack_geometry(tier1_task_001: Path, tmp_path: Path):
    # Load the task.
    task = load_task(tier1_task_001)
    # Build the problem text.
    text = render_problem(task)

    # Check the stack geometry is encoded correctly.
    assert "(base-layer layer_0)" in text
    assert "(above layer_1 layer_0)" in text
    assert "(can-attach" in text
    assert "(footprint" in text

    # Write the problem to disk.
    out = tmp_path / "tier1.pddl"
    # Write the problem to disk.
    write_problem(task, out, problem_name="tier1_task_001")
    # Parse the problem with UPF.
    PDDLReader().parse_problem(str(domain_path()), str(out))
