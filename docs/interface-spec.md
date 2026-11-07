# Module interface spec v0.1

What a module is, how modules bolt, plug and talk to each other, and how a task pack says which modules it needs. The aim is that any two people who follow this can swap parts, datasets and policies without talking to each other.

This is a proposal to be tested on the first build. Facts taken from the SO-ARM100 repo or the LeRobot docs are marked *(verified)*; everything else is a design choice.

## 1. Module types

| Type | Examples | Has actuators | Has cameras |
|---|---|---|---|
| `arm` | SO-101 follower (7.4V or 12V) | yes | no |
| `tool` | Parallel jaw, wide fabric jaw, hook, clothespin opener | optional | no |
| `camera` | Wrist camera, overhead camera, front camera | no | yes |
| `base` | LeKiwi-style omni base, fixed table clamp | optional | no |
| `lift` | Fixed column, cart shelf, motorised column | optional | no |
| `teleop` | SO-101 leader | sensors only | no |
| `compute` | Laptop, Raspberry Pi 5, Jetson | no | no |
| `power` | Wall supply, battery pack | no | no |

A robot is a set of module instances plus a profile name (section 6). A task pack targets a profile, not a specific robot.

## 2. Mechanical interface

### 2.1 Structure: 4040 aluminium extrusion

All structural mounting is to 4040 T-slot extrusion with M5 T-nuts. It is sold everywhere, needs no printing, and the SO-ARM100 repo already ships a 4040 base mount *(verified)*.

- Every module that mounts to structure has a printed **foot** with two or more M5 clearance holes spaced in multiples of 20 mm, so it bolts to one slot with T-nuts.
- Positions along the extrusion are specified in millimetres from the extrusion's near end. Profiles (section 6) give these numbers so cameras and arms land in the same place on every build.
- Table-clamp builds are still valid: the clamp is a `base` module and the arm's own base part is its foot.

### 2.2 Arm-to-tool: the wrist tool interface

On the SO-101 the gripper is the sixth servo (ID 6) *(verified)*, with the moving jaw screwed to its horn and the fixed jaw part of the wrist print.

- A `tool` module ships as two STL files that replace the stock jaws: `tool_fixed.stl` and `tool_moving.stl`, keeping the stock servo horn screw pattern and the fixed-jaw screw bosses. Swapping a tool means undoing those screws, no re-calibration.
- A tool must state its opening width, jaw depth and whether the jaw tips are padded, because policies trained with one jaw shape usually fail with another.
- A **powered tool** (for example a clothespin opener) carries its own STS3215 servo on the arm's bus with ID 7. It is wired through the same 3-pin cable chain.
- Quick-release (magnets plus locating pins) is deferred to v0.2 once a second tool exists.

### 2.3 Camera mounts

A `camera` module is a board or body plus a mount that fits one of two patterns:

- **Pattern A:** 32x32 mm UVC camera module, using the wrist and overhead mounts in the repo's `Optional/` folder *(verified that these mounts exist)*.
- **Pattern B:** anything with a 1/4"-20 tripod thread, on a printed foot per 2.1.

Camera pose matters more than camera model. A profile gives each camera's position and aim as a point and a target, both in millimetres from the arm's base origin. Builders tape-mark it; task packs record it.

## 3. Electrical interface

### 3.1 Power

Two voltage classes, never mixed on one servo board:

| Class | Who | Supply |
|---|---|---|
| `5V` | 7.4V-rated STS3215 arms, as the stock parts list runs them *(verified)*; leader arms | 5V wall supply, 5.5x2.1 mm barrel, centre positive |
| `12V` | 12V-rated STS3215 arms (need 12V 5A+ *(verified)*), bases, lifts | 12V wall supply or 3S battery, 5.5x2.1 mm barrel, centre positive |

Rules:
- One supply per servo board. Each arm keeps its own board and supply, so an arm is a self-contained unit you can unplug.
- A mobile build has one 12V battery and a 12V→5V buck converter rated at 5A or more per 5V arm.
- Every module labels its class on the foot.

### 3.2 Servo bus

- Each actuated module is one Feetech TTL bus on one Waveshare bus servo adapter, presented to the computer as one USB serial port *(the stock arm already works this way, verified)*.
- Servo IDs are reserved by module role, so modules can be chained onto one board later without ID clashes:

  | IDs | Role |
  |---|---|
  | 1–6 | arm joints (shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper) *(verified order)* |
  | 7 | powered tool |
  | 8–10 | base wheels |
  | 11 | lift |

  LeKiwi puts its wheels on 7–9 from memory; if you reuse its code, remap, or renumber in the config.

### 3.3 USB

- Cameras are UVC over USB. Fixed cameras plug into a powered hub; a wrist camera's cable runs along the arm with 10 cm of slack at the shoulder.
- Every USB device is referred to by a stable name, never a bare port index. On Linux use a udev rule per device; on macOS record the `usbmodem` path *(LeRobot's `lerobot-find-port` prints it, verified)*.

## 4. Software interface

The software layer is LeRobot. The spec only adds naming rules and a manifest on top of it.

### 4.1 Naming

- Joint keys follow LeRobot: `<joint>.pos`, for example `shoulder_pan.pos` *(verified)*. With more than one arm, prefix the module instance: `left_arm.shoulder_pan.pos`.
- Camera names are fixed vocabulary: `top`, `front`, `wrist`, `wrist_left`, `wrist_right`. A policy trained on `top` and `wrist` runs on any robot exposing those two names at the profile's poses.
- Module instance ids are the LeRobot `--robot.id` / `--teleop.id` values and own the calibration files *(verified mechanism)*. Convention: `<role>_<serial>`, for example `follower_01`, `leader_01`.

### 4.2 Robot manifest

Each physical robot has a `robot.yaml` describing which module instances it is made of. A small script turns it into the LeRobot robot config to pass on the command line (or a composite robot class, as LeKiwi does for base plus arm).

```yaml
name: tabletop-01
profile: P1-tabletop-1arm-2cam   # see section 6
modules:
  - type: arm
    instance: follower_01
    model: so101_follower
    voltage: 5V
    port: /dev/tty.usbmodem585A0076841
    tool: jaw_stock_v1
  - type: camera
    name: wrist
    model: uvc-32x32
    port: /dev/video2
    pose_mm: {at: [0, 0, 0], frame: wrist}
  - type: camera
    name: top
    model: webcam-1080p
    port: /dev/video0
    pose_mm: {at: [150, 0, 600], look_at: [250, 0, 0], frame: arm_base}
  - type: teleop
    instance: leader_01
    model: so101_leader
    port: /dev/tty.usbmodem575E0031751
```

### 4.3 Policy contract

A policy is compatible with a robot when:
1. the robot's profile matches the task pack's profile, and
2. the observation and action key sets are identical (LeRobot checks feature names and shapes when loading a policy).

Nothing else is promised. Different lighting, cloth or tool padding can still break it; the eval protocol in the task pack is how you find out.

## 5. Calibration and identity

- Each actuated module instance has its own calibration file, created once with `lerobot-calibrate` and keyed by its instance id *(verified)*.
- Moving an arm between robots keeps its calibration. Changing a tool does not require re-calibration; replacing a servo does.
- A module's foot carries a label with: type, instance id, voltage class, interface version (`MI-0.1`).

## 6. Hardware profiles

A profile is a named, exact layout. Task packs target one profile. The first three:

| Profile | Modules | Covers |
|---|---|---|
| `P1-tabletop-1arm-2cam` | 1 follower arm, `wrist` + `top` cameras, table clamp, 1 leader | sorting |
| `P2-tabletop-2arm-3cam` | 2 follower arms 400 mm apart, `wrist_left` + `wrist_right` + `top`, 2 leaders | folding |
| `P3-mobile-2arm-lift` | P2 on an omni base with a lift, plus `front` camera | hanging |

Each profile file states: extrusion lengths, foot positions in mm, camera poses in mm, workspace zone size, and which voltage class each slot takes. P1's numbers are fixed by the step-1 build once it works; P2 and P3 are written when those builds start.

## 7. Task pack format

A task pack is a folder (or repo) with this layout and a `taskpack.yaml`:

```
laundry-sort/
  taskpack.yaml
  README.md          # setup photo, tape marks, results
  hardware/          # STLs for any tool or fixture, plus links to module versions
  eval.md            # trial protocol and recorded success counts
```

```yaml
name: laundry-sort
version: 0.1.0
interface: MI-0.1
profile: P1-tabletop-1arm-2cam
tools:
  - jaw_stock_v1
tasks:
  - "Put the light item in the light tray"
  - "Put the dark item in the dark tray"
dataset: hf://<user>/laundry-sort-stage-b
policy:
  repo: hf://<user>/act-laundry-sort-b
  type: act
observation_keys: [observation.state, observation.images.wrist, observation.images.top]
eval:
  trials: 20
  pass: 14
  results:
    - {robot: tabletop-01, date: 2026-11-30, success: 15}
```

Rules:
- A task pack never bundles weights or videos directly; it links to Hugging Face so storage and versions are handled there.
- Results are appended by anyone who runs the eval on their own robot, with their robot name, so the pack accumulates evidence across builds.
- Bumping the pack's `profile` or `tools` is a major version change.

## 8. Versioning

- The interface spec uses `MI-<major>.<minor>`. Minor changes add things; major changes break fit or keys.
- A module declares the interface versions it implements. A task pack declares the one it was recorded on.

## 9. To validate on the first build

1. Whether the stock SO-101 base can take a 4040 foot without a new print, or needs an adapter STL.
2. Whether two screws are enough to swap a tool in under two minutes without disturbing the wrist camera.
3. Whether a manifest-to-LeRobot-config script is enough, or a composite robot class is needed for P2.
4. Camera pose tolerance: how far `top` can move before the stage-A policy fails. That number sets how precise the tape marks must be.
