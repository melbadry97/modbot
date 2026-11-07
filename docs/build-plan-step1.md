# Step 1 build plan: one arm pair that sorts laundry

Goal: one SO-101 leader + follower pair that picks small clothing items off a table and sorts them into two trays, with the dataset and trained policy published as task pack #1.

Sources, checked 5 Nov 2026:
- Parts and printing: the SO-ARM100 README, https://github.com/TheRobotStudio/SO-ARM100
- Software: the LeRobot docs, https://huggingface.co/docs/lerobot/so101 and https://huggingface.co/docs/lerobot/il_robots

Anything marked *(estimate)* is my own figure, not from those pages.

## 1. Parts list

### Arms (prices as listed in the README, US column)

| Part | Qty | Unit | Notes |
|---|---|---|---|
| Feetech STS3215 servo, 7.4V, 1/345 gear (C001) | 7 | $13.89 | 6 for the follower, 1 for the leader |
| Feetech STS3215 servo, 7.4V, 1/191 gear (C044) | 2 | $13.89 | leader |
| Feetech STS3215 servo, 7.4V, 1/147 gear (C046) | 3 | $13.89 | leader |
| Motor control board (Waveshare bus servo adapter) | 2 | $10.60 | one per arm |
| Power supply, 5V | 2 | $10 | one per arm |
| USB-C cables, 2-pack | 1 | $7 | |
| Table clamps, 4-pack | 1 | $9 | |
| Screwdriver set (Phillips #0 and #1) | 1 | $6 | skip if you own them |
| **Total listed** | | **$229.88** | EU total listed: €226.30 |

The README links a seller for each line, in US, EU, China and Japan.

### Extras for this task

| Part | Qty | Cost | Notes |
|---|---|---|---|
| PLA+ filament, 1 kg | 1 | ~$20 *(estimate)* | enough for both arms |
| USB camera for the wrist | 1 | ~$15–30 *(estimate)* | the repo has mounts for 32x32 mm UVC modules and one webcam model |
| USB webcam, overhead | 1 | ~$15–30 *(estimate)* | the repo has an overhead mount |
| Two shallow trays, one light and one dark | 2 | household | low sides, so the arm can reach over them |
| Plain table mat | 1 | household | one colour, so clothes stand out |

**All in: roughly $290–320** *(estimate)*, less if you already own a webcam.

### One choice to make before ordering

The follower can be built with 12V servos instead of 7.4V. The README gives stall torque as 30 kg·cm for 12V versus 16.5 kg·cm for 7.4V, and says the 12V build needs a 12V 5A+ power supply. The leader is always 7.4V.

Recommendation: build the 7.4V follower now. It is what the listed prices and one power supply type cover, and the README calls it sufficient. Revisit 12V when you add the second arm for folding.

### No printer?

The README lists vendors selling printed frames, electronics kits or full kits: Seeed Studio, WowRobo, RobotEd (Switzerland), Robonine, PartaBot (US), ForgeMotion Labs (US), RoboSEasy (South Korea), NeoBot (China) and Autodiscovery (EU). It shows no prices for them.

## 2. Printing

Settings from the README:
- PLA+, 0.4 mm nozzle at 0.2 mm layers (or 0.6 mm nozzle at 0.4 mm layers), 15% infill.
- Supports everywhere, ignoring slopes over 45° from horizontal.
- One ready-arranged file per arm:
  - 220x220 mm bed: `STL/SO101/Follower/Ender_Follower_SO101.stl` and `STL/SO101/Leader/Ender_Leader_SO101.stl`
  - 205x250 mm bed: `STL/SO101/Follower/Prusa_Follower_SO101.stl` and `STL/SO101/Leader/Prusa_Leader_SO101.stl`
- Print the gauges in `STL/Gauges/` first to check a servo fits your printer's tolerances.
- Also print one wrist camera mount and the overhead camera mount from the `Optional/` folder.

Expect about a day of printing per arm *(estimate)*.

## 3. Build order

1. **Order parts and start printing.** Shipping is usually the slowest step.
2. **Install the software** while you wait (section 4).
3. **Set motor IDs before assembly.** Each servo is connected to the board alone, one at a time, starting with the gripper (ID 6). The script prompts you for each one.
4. **Label the leader's servos**, because they have different gears:

   | Joint | ID | Gear |
   |---|---|---|
   | Shoulder pan | 1 | 1/191 |
   | Shoulder lift | 2 | 1/345 |
   | Elbow flex | 3 | 1/191 |
   | Wrist flex | 4 | 1/147 |
   | Wrist roll | 5 | 1/147 |
   | Gripper | 6 | 1/147 |

   The follower uses 1/345 servos on every joint.
5. **Assemble both arms** following the LeRobot SO-101 page, then clamp them to the table.
6. **Calibrate** each arm, then **teleoperate** without cameras to confirm the follower mirrors the leader.
7. **Mount the cameras**, fix their positions, and teleoperate again with the camera view on.

## 4. Software commands

Use Python 3.12. Replace the port names with the ones `lerobot-find-port` reports.

Install:
```bash
pip install 'lerobot[core_scripts]' 'lerobot[training]' 'lerobot[feetech]'
```

Find each arm's port (run once per arm; on Linux also `sudo chmod 666` the port):
```bash
lerobot-find-port
```

Set motor IDs:
```bash
lerobot-setup-motors --robot.type=so101_follower --robot.port=FOLLOWER_PORT
```
```bash
lerobot-setup-motors --teleop.type=so101_leader --teleop.port=LEADER_PORT
```

Calibrate (keep the same ids for every later command):
```bash
lerobot-calibrate --robot.type=so101_follower --robot.port=FOLLOWER_PORT --robot.id=sorter_follower
```
```bash
lerobot-calibrate --teleop.type=so101_leader --teleop.port=LEADER_PORT --teleop.id=sorter_leader
```

Teleoperate with cameras:
```bash
lerobot-teleoperate \
    --robot.type=so101_follower --robot.port=FOLLOWER_PORT --robot.id=sorter_follower \
    --robot.cameras="{ wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}" \
    --teleop.type=so101_leader --teleop.port=LEADER_PORT --teleop.id=sorter_leader \
    --display_data=true
```

Record demonstrations (log in first with `hf auth login`):
```bash
lerobot-record \
    --robot.type=so101_follower --robot.port=FOLLOWER_PORT --robot.id=sorter_follower \
    --robot.cameras="{ wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}" \
    --teleop.type=so101_leader --teleop.port=LEADER_PORT --teleop.id=sorter_leader \
    --display_data=true \
    --dataset.repo_id=${HF_USER}/laundry-sort-stage-a \
    --dataset.no_stamp=true \
    --dataset.num_episodes=50 \
    --dataset.episode_time_s=30 \
    --dataset.reset_time_s=15 \
    --dataset.single_task="Put the clothing item in the tray"
```
Keys while recording: right arrow or `n` ends the episode, left arrow or `r` re-records it, Escape or `q` stops and uploads.

Train an ACT policy (`cuda` for an NVIDIA GPU, `mps` for Apple silicon):
```bash
lerobot-train \
    --dataset.repo_id=${HF_USER}/laundry-sort-stage-a \
    --policy.type=act \
    --output_dir=outputs/train/act_laundry_sort_a \
    --job_name=act_laundry_sort_a \
    --policy.device=cuda \
    --policy.repo_id=${HF_USER}/act-laundry-sort-a
```
The docs say training takes several hours. With no suitable GPU, they point to a Google Colab notebook for ACT training, or Hugging Face Jobs via `--job.target=a10g-small`.

Run the trained policy on the robot:
```bash
lerobot-rollout \
    --strategy.type=base \
    --policy.path=${HF_USER}/act-laundry-sort-a \
    --robot.type=so101_follower --robot.port=FOLLOWER_PORT --robot.id=sorter_follower \
    --robot.cameras="{ wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}" \
    --task="Put the clothing item in the tray" \
    --duration=60
```

## 5. The sorting task, in two stages

The targets and episode counts for stage B are my proposals. The "50 episodes, 10 per location" starting point is from the LeRobot docs.

**Setup for both stages**
- Small, light items only: socks, washcloths, baby clothes. The arm's reach and payload are small.
- Mark a pickup zone of about 25x25 cm in front of the arm, with a tray on each side within reach.
- Fix the cameras, the lighting and the tray positions. Mark them with tape so the setup can be rebuilt.

**Stage A: one item, one tray**
- Task: pick up the single item in the zone and drop it in the tray.
- Data: 50 episodes, 10 at each of 5 positions in the zone.
- Pass: 16 of 20 trials succeed, with items placed at positions you choose at random.

**Stage B: lights and darks**
- Task: light items go in the light tray, dark items in the dark tray, one item per episode.
- Data: 100 episodes, 50 light and 50 dark, spread over the same 5 positions.
- Use two task strings, "Put the light item in the light tray" and "Put the dark item in the dark tray".
- Pass: 14 of 20 trials succeed, counting a wrong tray as a failure.

**Data habits from the docs**
- You should be able to do the task yourself looking only at the camera images. If you can't, move the cameras.
- Grasp the same way every time. Add variation only once grasping is reliable.
- Watch the frame-rate report during recording. A loop slower than 30 fps corrupts the timing.

## 6. What "done" looks like: task pack #1

A public folder or repo containing:
- `README.md`: the setup photo, tape-mark measurements, and the pass results.
- `hardware/`: links to the exact arm version, plus STL files for any mount or tray you designed.
- `dataset`: link to the Hugging Face dataset.
- `policy`: link to the trained checkpoint.
- `eval.md`: the 20-trial protocol and your success counts.

If a second person can build from that folder and reach a similar success rate after recording their own 50 episodes, step 1 has worked.
