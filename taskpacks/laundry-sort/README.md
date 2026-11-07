# Task pack: laundry-sort

Pick small clothing items off a table and sort them into two trays. Profile `P1-tabletop-1arm-2cam`.

Full setup, data plan and commands: `docs/build-plan-step1.md`, section 5.

## Setup

- One follower arm clamped to the table, pickup zone 25x25 cm in front of it, one shallow tray on each side within reach.
- Plain single-colour mat. Fixed lighting. Cameras `wrist` and `top` at the profile's poses.
- Tape-mark the arm base, both trays and the zone corners, and photograph the setup from above. Put the photo here as `setup.jpg`.

## Stages

- **A:** one item, one tray. 50 episodes. Pass is 16 of 20 trials.
- **B:** lights into the light tray, darks into the dark tray. 100 episodes. Pass is 14 of 20; a wrong tray is a failure.

## Results

See `results` in `taskpack.yaml`. Append yours by pull request.
