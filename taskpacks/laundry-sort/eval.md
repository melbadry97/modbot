# Evaluation protocol: laundry-sort

Run after training, on the same robot and setup the data was recorded on. One stage at a time.

## Before the trials

1. Rebuild the setup to the tape marks and compare with `setup.jpg`.
2. Use a fresh set of items of the same kind as the training set, not the exact items you recorded with.
3. Write down 20 placement positions inside the pickup zone before starting, drawn at random. For stage B, alternate light and dark items, 10 each.

## Each trial

1. Place the item at the listed position, flat, any orientation.
2. Start the policy with the stage's task string and a 60 s duration.
3. Record one of: **success** (item fully inside the correct tray, arm stopped without a collision), **wrong tray**, **dropped**, **no grasp**, **timeout**, **unsafe** (you had to intervene).
4. Reset the trays and the item. Do not touch the cameras or lighting between trials.

## Reporting

Count successes out of 20. Append to `taskpack.yaml`:

```yaml
- {stage: a, robot: tabletop-01, date: 2026-12-01, success: 15, notes: "2 no-grasp on dark socks, 3 dropped"}
```

Include the failure breakdown in `notes`. A result counts as passing when it meets the stage's `pass` number.
