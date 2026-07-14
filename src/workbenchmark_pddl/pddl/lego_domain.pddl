;; LEGO Duplo assembly domain for WorkBenchMark (Project P1)
;; Area-based v1 model: pick area, assembly area, vertical stacking.

(define (domain lego-assembly)
  (:requirements :strips :typing)

  (:types
    brick
    gripper
    area
    grid_loc    ; reserved for future stud-level modeling
  )

  (:predicates
    (stacked-on ?top - brick ?bottom - brick)
    (on-table ?b - brick)
    (clear ?b - brick)
    (graspable ?b - brick)
    (in-pick-area ?b - brick)
    (in-asm-area ?b - brick)
    (target-pose ?b - brick)
    (holding ?g - gripper ?b - brick)
    (gripper-empty ?g - gripper)
  )

  ;; Pick a graspable brick from the pick area.
  (:action pick
    :parameters (?g - gripper ?b - brick)
    :precondition (and
      (gripper-empty ?g)
      (in-pick-area ?b)
      (graspable ?b)
      (clear ?b)
    )
    :effect (and
      (holding ?g ?b)
      (not (gripper-empty ?g))
      (not (in-pick-area ?b))
      (not (on-table ?b))
      (not (graspable ?b))
      (not (clear ?b))
    )
  )

  ;; Place a held brick on the assembly-area table / baseplate.
  (:action place
    :parameters (?g - gripper ?b - brick)
    :precondition (holding ?g ?b)
    :effect (and
      (gripper-empty ?g)
      (in-asm-area ?b)
      (on-table ?b)
      (clear ?b)
      (graspable ?b)
      (not (holding ?g ?b))
    )
  )

  ;; Stack a held brick onto another brick in the assembly area.
  (:action stack
    :parameters (?g - gripper ?top - brick ?bottom - brick)
    :precondition (and
      (holding ?g ?top)
      (clear ?bottom)
      (in-asm-area ?bottom)
    )
    :effect (and
      (gripper-empty ?g)
      (stacked-on ?top ?bottom)
      (clear ?top)
      (in-asm-area ?top)
      (not (holding ?g ?top))
      (not (clear ?bottom))
      (not (on-table ?top))
    )
  )
)
