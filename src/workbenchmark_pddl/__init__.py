"""PDDL domain modeling for WorkBenchMark LEGO Duplo assembly (AIfR Project P1)."""

from workbenchmark_pddl.task import BrickSpec, TaskSpec, load_task

__version__ = "0.1.0"

# Export the public API.
__all__ = ["BrickSpec", "TaskSpec", "load_task", "__version__"]

