#!/usr/bin/env python
"""Verify the Project P1 toolchain: core dependencies and a PDDL planner engine.

Exits 0 when the environment is ready, 1 otherwise.
"""

from __future__ import annotations

import importlib

REQUIRED = {
    "tampanda": "TAMPanda simulation (editable local install)",
    "unified_planning": "unified-planning PDDL API",
    "yaml": "PyYAML task-spec parsing",
    "numpy": "numeric geometry",
}


def check_imports() -> list[str]:
    problems: list[str] = []
    for mod, why in REQUIRED.items():
        try:
            m = importlib.import_module(mod)
            version = getattr(m, "__version__", "?")
            print(f"  OK   {mod:<18} {version}  ({why})")
        except Exception as exc:  # noqa: BLE001 - report any import failure
            problems.append(mod)
            print(f"  FAIL {mod:<18} {exc.__class__.__name__}: {exc}")
    return problems


def check_planner() -> list[str]:
    try:
        import unified_planning.shortcuts as up

        up.get_environment().credits_stream = None
        with up.OneshotPlanner(name="pyperplan"):
            print("  OK   planner engine    pyperplan available")
        return []
    except Exception as exc:  # noqa: BLE001 - report any engine failure
        print(f"  FAIL planner engine    {exc.__class__.__name__}: {exc}")
        return ["pyperplan"]


def main() -> int:
    print("Project P1 environment check")
    print("- core imports:")
    problems = check_imports()
    print("- planner engine:")
    problems += check_planner()

    if problems:
        print(f"\nENV NOT READY -> {', '.join(problems)}")
        return 1
    print("\nENV OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
