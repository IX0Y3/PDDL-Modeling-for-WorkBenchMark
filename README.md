# PDDL Modeling for WorkBenchMark

**Project P1** — AI for Robotics, Summer Semester 2026 (RWTH Aachen)

Design a PDDL domain for LEGO Duplo assembly, plan with a general-purpose
planner, and execute in [TAMPanda](../tampanda) via `DomainBridge`.

- Benchmark: [WorkBenchMark](https://workbenchmark.github.io)
- Paper: [arXiv:2606.19358](https://arxiv.org/abs/2606.19358)

## What This Project Does

WorkBenchMark ships an Assembly-by-Disassembly (ABD) baseline. We model the
assembly task symbolically in PDDL and let a classical planner produce the
sequence. The generated plan is executed in TAMPanda through `DomainBridge`
and `PickPlaceExecutor`.

Pipeline: **YAML task spec → PDDL problem → planner → action plan → MuJoCo execution**

Reuses the TAMPanda blocks-world pattern (`blocks_bridge.py`). All P1 code
lives in this repo; TAMPanda is an editable local dependency.

## Scope

| In scope | Out of scope |
|---|---|
| Tier 1 (2-brick) and Tier 2 (3–5 brick) vertical stacks | Tier 3–4, real robot |
| Ground-truth poses from YAML | Perception (GroundingDINO, SAM, …) |
| MuJoCo simulation via TAMPanda | Modifying TAMPanda itself |

## Phases

| Phase | Goal | Status |
|---|---|---|
| **1 — Setup** | Repo, `pyproject.toml`, package skeleton, env smoke tests | done |
| **2 — Symbolic layer** | `lego_domain.pddl`, YAML parser, problem generator | in progress |
| **3 — Execution & evaluation** | `DomainBridge` wiring, batch runner, metrics, failure analysis | pending |

**Phase 2 deliverables:** PDDL domain with `pick` / `place` / `stack` actions;
YAML parser for WorkBenchMark `blocks[]` specs; problem generator from
initial + goal YAML.

**Phase 3 deliverables:** predicate grounding and motion executors in TAMPanda;
systematic evaluation on Tier 1–2 (N = 20 tasks per tier).

## Evaluation Metrics

- **Planning success** — planner finds a valid plan
- **Execution success** — all actions succeed in TAMPanda
- **Planning time & plan length** — vs. ABD baseline where available
- **Failure analysis** — which task structures expose model gaps

## Setup

Python 3.10+, TAMPanda at `../tampanda`.

```bash
cd /work/rleap1/aifr/prak4/Project
source /work/rleap1/aifr/prak4/venv/bin/activate
pip install -e ../tampanda
pip install -e .[dev]
python scripts/check_env.py
pytest
```

## Progress

| Phase | Status | Notes |
|---|---|---|
| 1 — Setup | done | Project scaffold and environment tests |
| 2 — Symbolic layer | in progress | `lego_domain.pddl` and domain-parse tests |
| 3 — Execution & evaluation | pending | — |
