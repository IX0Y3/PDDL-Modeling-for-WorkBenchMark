"""Compile a WorkBenchMark TaskSpec into a PDDL problem string."""

from __future__ import annotations

from pathlib import Path

from workbenchmark_pddl.pddl_names import default_problem_name
from workbenchmark_pddl.problem_builder import ProblemBuilder
from workbenchmark_pddl.task import TaskSpec


# Public entry: TaskSpec → PDDL problem text.
def render_problem(task: TaskSpec, *, problem_name: str | None = None) -> str:
    # Build the problem text.
    name = problem_name or default_problem_name(task)
    builder = ProblemBuilder.from_task(task)
    # Return the problem text.
    return builder.render(name)


# Write the problem text to disk and return the path.
def write_problem(
    task: TaskSpec,
    path: str | Path,
    *,
    problem_name: str | None = None,
) -> Path:
    # Write the problem text to disk.
    path = Path(path)
    path.write_text(render_problem(task, problem_name=problem_name), encoding="utf-8")
    # Return the path.
    return path


# Path to the bundled domain file.
def domain_path() -> Path:
    return Path(__file__).resolve().parent / "pddl" / "lego_domain.pddl"
