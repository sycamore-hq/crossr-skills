# Premise

Two failures on one premise mean the premise is the bug.

## Rules

DP-01  When two fixes that share one premise fail the same gate (the same test, check, or verdict id), stop patching.

DP-02  State the shared premise in one sentence. Take a rerunnable census of which actors hold the imbalance, so systematic skew can be told apart from incidental distribution, and name the mechanism that repeatedly assigns it to them.

DP-03  Remove that assignment mechanism by eliminating the responsibility, redistributing or rotating it, or giving it a single owner where appropriate, then redesign from first principles. Unique responsibilities the failures do not implicate stay. No further fix until the mechanism is addressed.

## How

Example: two retry tweaks on a job runner both fail the same flake check. The premise is "the runner owns retry policy." The census shows the scheduler's affinity rule sends nine in ten retries to one node. The affinity rule is the mechanism. Remove it. Do not tune retry number three.

A census is a script or query whose output anyone can regenerate. A list of component names is not a census. If building one by hand is not obvious, build the tool that does it.

Asymmetry is not a defect by itself. Target only the assignment the repeated failures implicate.

Redesign from first principles: do not bolt the requirement onto the old design. Ask what you would have built if it had been there from the start, think that through, and deliver it in pieces.
