"""Stud footprints and attach checks for Duplo brick types."""

from __future__ import annotations

from workbenchmark_pddl.grid import DiscretePose

# Brick type string from YAML → size in studs (width, depth) at yaw 0°.
BRICK_SIZE_STUDS: dict[str, tuple[int, int]] = {
    "brick_2x2": (2, 2),
    "brick_4x2": (4, 2),
}

# Minimum overlapping studs required for a valid stack connection.
MIN_OVERLAP_STUDS = 1

# Relative stud cells covered by a brick of size (w, d), measured from its center cell.
def footprint_offsets(width: int, depth: int) -> list[tuple[int, int]]:

    # Initialize an empty list to store the offsets
    offsets: list[tuple[int, int]] = []

    # Iterate over the width and depth of the brick
    for dx in range(-width // 2, width // 2):
        for dy in range(-depth // 2, depth // 2):
            # Add the offset to the list
            offsets.append((dx, dy))

    # Return the list of offsets
    return offsets


# Absolute stud cells covered when a brick sits at pose (center stud + rot).
def covered_studs(brick_type: str, pose: DiscretePose) -> set[tuple[int, int]]:

    # Get the width and depth of the brick
    width, depth = BRICK_SIZE_STUDS[brick_type]

    # If the brick is rotated 90 degrees, swap the width and depth
    if pose.rot == 90:
        width, depth = depth, width

    # Return the set of covered studs
    return {
        (pose.stud_x + dx, pose.stud_y + dy)
        for dx, dy in footprint_offsets(width, depth)
    }


# True if top/bottom footprints overlap enough to stud-connect.
def can_attach(
    top_type: str,
    top_pose: DiscretePose,
    bottom_type: str,
    bottom_pose: DiscretePose,
) -> bool:

    # Get the overlap of the covered studs
    overlap = covered_studs(top_type, top_pose) & covered_studs(
        bottom_type, bottom_pose
    )

    # Check if the overlap is greater than or equal to the minimum overlap studs
    return len(overlap) >= MIN_OVERLAP_STUDS
