"""Unit tests for ProblemBuilder (no UPF — fast structural checks)."""

from pathlib import Path

from workbenchmark_pddl.pddl_names import stud_object
from workbenchmark_pddl.problem_builder import ProblemBuilder
from workbenchmark_pddl.task import load_task

# Test the from_task method for tier1 tasks.
# Should set max_layer to 1, have 2 goal poses, 2 init poses, and anchor studs.
def test_from_task_tier1_layers_and_pick_origin(tier1_task_001: Path):
    # Load the task.
    task = load_task(tier1_task_001)
    builder = ProblemBuilder.from_task(task)

    # Check the max layer, goal poses, and init poses.
    assert builder.max_layer == 1
    assert len(builder.goal_poses) == 2
    assert len(builder.init_poses) == 2

    # Pick bricks use local z_origin → layer 0.
    for pose in builder.init_poses.values():
        assert pose.layer == 0

    # Goal stack: base layer 0, top layer 1, same XY.
    base = builder.goal_poses["4x2_brick_1"]
    top = builder.goal_poses["4x2_brick_2"]
    assert base.layer == 0
    assert top.layer == 1
    assert (base.stud_x, base.stud_y) == (top.stud_x, top.stud_y)
    assert (base.stud_x, base.stud_y) in builder.anchor_studs

# Test the goal lines for encoding assembly poses.
# Should encode each goal pose with at-stud, at-layer, oriented, and in-area.
def test_goal_lines_encode_assembly_poses(tier1_task_001: Path):
    # Load the task.
    task = load_task(tier1_task_001)
    # Build the problem builder.
    builder = ProblemBuilder.from_task(task)
    # Build the goal lines.
    goal = "\n".join(builder.goal_lines())

    # Check each goal pose is encoded correctly.
    for brick in task.goal_blocks:
        pose = builder.goal_poses[brick.name]
        assert f"(at-stud b_{brick.name} {stud_object(pose.stud_x, pose.stud_y)})" in goal
        assert f"(at-layer b_{brick.name} layer_{pose.layer})" in goal
        assert f"(oriented b_{brick.name} rot_{pose.rot})" in goal
        assert f"(in-area b_{brick.name} assembly_area)" in goal

# Test the brick init lines for encoding pick area.
# Should encode each initial block with in-area and clear.
def test_brick_init_lines_are_in_pick_area(tier1_task_001: Path):
    # Load the task.
    task = load_task(tier1_task_001)
    # Build the problem builder.
    builder = ProblemBuilder.from_task(task)
    # Get the first initial block.
    brick = task.initial_blocks[0]
    # Build the init lines.
    init = "\n".join(builder.brick_init_lines(brick))

    # Check the init lines are encoded correctly.
    assert f"(in-area b_{brick.name} pick_area)" in init
    assert f"(clear b_{brick.name})" in init
    assert f"(is-type b_{brick.name}" in init

# Test the tier3 task has multiple goal anchors.
# Should have more than one distinct XY anchor, max layer >= 1, and can-attach/footprint lines.
def test_tier3_has_multiple_goal_anchors(tier3_task_001: Path):
    # Load the task.
    task = load_task(tier3_task_001)
    # Build the problem builder.
    builder = ProblemBuilder.from_task(task)
    # Get the goal anchors.
    goal_anchors = {
        (pose.stud_x, pose.stud_y) for pose in builder.goal_poses.values()
    }
    # Multi-column layout → more than one distinct XY anchor.
    assert len(goal_anchors) > 1
    assert builder.max_layer >= 1
    assert any("can-attach" in line for line in builder.can_attach_lines())
    assert any("footprint" in line for line in builder.footprint_lines())

# Test the render method contains required sections.
# Should include problem, objects, init, and goal sections.
def test_render_contains_required_sections(tier2_task_001: Path):
    # Load the task.
    task = load_task(tier2_task_001)
    # Build the problem builder.
    text = ProblemBuilder.from_task(task).render("tier2_task_001")

    # Check the render method contains the required sections.
    assert "(define (problem tier2_task_001)" in text
    assert "(:objects" in text
    assert "(:init" in text
    assert "(:goal (and" in text
    assert "(above layer_1 layer_0)" in text
