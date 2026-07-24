"""Build PDDL problem sections from a quantized TaskSpec."""

from __future__ import annotations

from workbenchmark_pddl.geometry import (
    BRICK_SIZE_STUDS,
    can_attach,
    covered_studs,
    footprint_offsets,
)
from workbenchmark_pddl.grid import DiscretePose, quantize_brick
from workbenchmark_pddl.pddl_names import (
    ASSEMBLY_AREA,
    DOMAIN_NAME,
    GRIPPER_NAME,
    PICK_AREA,
    brick_object,
    layer_object,
    rot_object,
    stud_object,
    type_object,
)
from workbenchmark_pddl.task import BrickSpec, TaskSpec

# ProblemBuilder class to build PDDL problem sections from a quantized TaskSpec.
class ProblemBuilder:

    # Initialize the ProblemBuilder with task data and derived poses.
    def __init__(
        self,
        task: TaskSpec,
        init_poses: dict[str, DiscretePose],
        goal_poses: dict[str, DiscretePose],
        studs: set[tuple[int, int]],
        anchor_studs: set[tuple[int, int]],
        max_layer: int,
    ) -> None:
        # Store task and derived poses.
        self.task = task
        self.init_poses = init_poses
        self.goal_poses = goal_poses
        self.studs = studs
        # Brick center cells only — used for can-attach.
        self.anchor_studs = anchor_studs
        self.max_layer = max_layer

    # Quantize poses and gather studs/layers needed for this task.
    @classmethod
    def from_task(cls, task: TaskSpec) -> ProblemBuilder:
        # Pick-area bricks: local z so they sit on layer 0.
        init_poses: dict[str, DiscretePose] = {}
        for brick in task.initial_blocks:
            init_poses[brick.name] = quantize_brick(brick, z_origin=brick.pos[2])

        # Goal poses use world z with base at z≈0 → layer 0, 1, …
        goal_poses: dict[str, DiscretePose] = {}
        for brick in task.goal_blocks:
            goal_poses[brick.name] = quantize_brick(brick)

        # Gather anchor studs and covered studs for can-attach.
        anchor_studs: set[tuple[int, int]] = set()
        studs: set[tuple[int, int]] = set()

        # Add anchor studs and covered studs for initial blocks.
        for brick in task.initial_blocks:
            pose = init_poses[brick.name]
            anchor_studs.add((pose.stud_x, pose.stud_y))
            studs |= covered_studs(brick.type, pose)

        # Add anchor studs and covered studs for goal blocks.
        for brick in task.goal_blocks:
            pose = goal_poses[brick.name]
            anchor_studs.add((pose.stud_x, pose.stud_y))
            studs |= covered_studs(brick.type, pose)

        studs |= anchor_studs

        # Determine the maximum layer from goal poses.
        max_layer = 0
        if goal_poses:
            max_layer = max(pose.layer for pose in goal_poses.values())

        # Return a new ProblemBuilder instance.
        return cls(task, init_poses, goal_poses, studs, anchor_studs, max_layer)

    # Full PDDL problem text.
    def render(self, problem_name: str) -> str:
        # Build the PDDL problem text.
        lines: list[str] = [
            ";; Auto-generated from WorkBenchMark task"
            + (f" ({self.task.source.name})" if self.task.source else ""),
            f"(define (problem {problem_name})",
            f"  (:domain {DOMAIN_NAME})",
            "",
            "  (:objects",
        ]
        # Add object lines for bricks, types, gripper, studs, layers, and rotations.
        lines.extend(self.object_lines())
        lines.append("  )")
        lines.append("")
        lines.append("  (:init")
        lines.extend(self.init_lines())
        lines.append("  )")
        lines.append("")
        lines.append("  (:goal (and")
        lines.extend(self.goal_lines())
        lines.append("  ))")
        lines.append(")")
        lines.append("")
        return "\n".join(lines)

    # Build the object lines for bricks, types, gripper, studs, layers, and rotations.
    def object_lines(self) -> list[str]:
        lines: list[str] = []

        for brick in self.task.initial_blocks:
            lines.append(f"    {brick_object(brick.name)} - brick")

        for brick_type in sorted(BRICK_SIZE_STUDS):
            lines.append(f"    {type_object(brick_type)} - brick-type")

        lines.append(f"    {GRIPPER_NAME} - endeffector")

        for sx, sy in sorted(self.studs):
            lines.append(f"    {stud_object(sx, sy)} - stud")

        for layer in range(self.max_layer + 1):
            lines.append(f"    {layer_object(layer)} - layer")

        for rot in (0, 90):
            lines.append(f"    {rot_object(rot)} - rot")

        lines.append(f"    {PICK_AREA} - area")
        lines.append(f"    {ASSEMBLY_AREA} - area")
        return lines

    # Build the init lines for gripper, areas, layers, and footprint/can-attach.
    def init_lines(self) -> list[str]:
        lines: list[str] = [
            f"    (gripper-empty {GRIPPER_NAME})",
            f"    (area-pick {PICK_AREA})",
            f"    (area-assembly {ASSEMBLY_AREA})",
            f"    (base-layer {layer_object(0)})",
        ]

        # Consecutive layer neighbours for stack.
        for layer in range(1, self.max_layer + 1):
            lines.append(
                f"    (above {layer_object(layer)} {layer_object(layer - 1)})"
            )

        lines.extend(self.footprint_lines())
        lines.extend(self.can_attach_lines())

        # Occupancy grid: free everywhere, then mark pick anchors occupied.
        occupied: set[tuple[int, int, int]] = set()
        for brick in self.task.initial_blocks:
            pose = self.init_poses[brick.name]
            occupied.add((pose.stud_x, pose.stud_y, pose.layer))

        for sx, sy in sorted(self.studs):
            for layer in range(self.max_layer + 1):
                s = stud_object(sx, sy)
                l = layer_object(layer)
                if (sx, sy, layer) in occupied:
                    lines.append(f"    (occupied {s} {l})")
                else:
                    lines.append(f"    (free {s} {l})")

        for brick in self.task.initial_blocks:
            lines.extend(self.brick_init_lines(brick))

        return lines

    # Build the init lines for a specific brick.
    def brick_init_lines(self, brick: BrickSpec) -> list[str]:
        pose = self.init_poses[brick.name]
        b = brick_object(brick.name)
        s = stud_object(pose.stud_x, pose.stud_y)
        l = layer_object(pose.layer)
        r = rot_object(pose.rot)
        t = type_object(brick.type)
        return [
            f"    (is-type {b} {t})",
            f"    (at-stud {b} {s})",
            f"    (at-layer {b} {l})",
            f"    (oriented {b} {r})",
            f"    (in-area {b} {PICK_AREA})",
            f"    (clear {b})",
        ]

    # Build the goal lines for a specific brick.
    def goal_lines(self) -> list[str]:
        # Exact assembly poses — enough for Tier 3 multi-column / rotated goals.
        lines: list[str] = []
        for brick in self.task.goal_blocks:
            pose = self.goal_poses[brick.name]
            b = brick_object(brick.name)
            lines.append(
                f"    (at-stud {b} {stud_object(pose.stud_x, pose.stud_y)})"
            )
            lines.append(f"    (at-layer {b} {layer_object(pose.layer)})")
            lines.append(f"    (oriented {b} {rot_object(pose.rot)})")
            lines.append(f"    (in-area {b} {ASSEMBLY_AREA})")
        return lines

    # Build the footprint lines for each brick type and rotation.
    def footprint_lines(self) -> list[str]:
        lines: list[str] = []
        for brick_type, (width, depth) in sorted(BRICK_SIZE_STUDS.items()):
            for rot in (0, 90):
                w, d = (depth, width) if rot == 90 else (width, depth)
                offsets = footprint_offsets(w, d)
                t = type_object(brick_type)
                r = rot_object(rot)
                for ax, ay in sorted(self.anchor_studs):
                    for dx, dy in offsets:
                        cell = (ax + dx, ay + dy)
                        if cell not in self.studs:
                            continue
                        lines.append(
                            "    (footprint "
                            f"{t} {r} {stud_object(ax, ay)} "
                            f"{stud_object(*cell)})"
                        )
        return lines

    # Build the can-attach lines for each brick type and rotation.
    def can_attach_lines(self) -> list[str]:
        # Only brick-center anchors — stack uses at-stud, not every footprint cell.
        lines: list[str] = []
        types = sorted(BRICK_SIZE_STUDS)
        anchors = sorted(self.anchor_studs)
        for t_top in types:
            for t_bot in types:
                for r_top in (0, 90):
                    for r_bot in (0, 90):
                        for top_xy in anchors:
                            for bot_xy in anchors:
                                top_pose = DiscretePose(
                                    stud_x=top_xy[0],
                                    stud_y=top_xy[1],
                                    layer=1,
                                    rot=r_top,
                                )
                                bot_pose = DiscretePose(
                                    stud_x=bot_xy[0],
                                    stud_y=bot_xy[1],
                                    layer=0,
                                    rot=r_bot,
                                )
                                if not can_attach(t_top, top_pose, t_bot, bot_pose):
                                    continue
                                lines.append(
                                    "    (can-attach "
                                    f"{type_object(t_top)} {rot_object(r_top)} "
                                    f"{stud_object(*top_xy)} "
                                    f"{type_object(t_bot)} {rot_object(r_bot)} "
                                    f"{stud_object(*bot_xy)})"
                                )
        return lines
