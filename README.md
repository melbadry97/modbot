# modbot

Low-cost, modular household robots that anyone can print, buy and build at home, and that learn tasks from demonstration.

The first three tasks, in order of difficulty:

1. **Sort laundry** from a pile into trays (one arm).
2. **Fold laundry** on a table (two arms).
3. **Hang laundry** on a drying rack (two arms on a mobile base with a lift).

Each task ships as a **task pack**: the printable tools, a dataset, a trained policy and an evaluation protocol, so a second person can rebuild it and check their success rate.

## How it works

- **Hardware:** [SO-101](https://github.com/TheRobotStudio/SO-ARM100) arms (3D printed, six Feetech servos, about $120 each) on 4040 aluminium extrusion, with USB cameras.
- **Learning:** [LeRobot](https://huggingface.co/docs/lerobot). Demonstrations are recorded by teleoperating with a leader arm, then an ACT policy is trained and run on the same robot.
- **Modularity:** arms, tools, cameras, bases and lifts are modules with fixed mechanical, electrical and software interfaces. A **profile** is an exact layout of modules; a task pack targets a profile, not a specific robot.

## Repository layout

| Path | What |
|---|---|
| `docs/build-plan-step1.md` | Parts list, printing settings, build order, commands and the two-stage sorting task |
| `docs/interface-spec.md` | Module interface spec v0.1: mounting, tools, cameras, power, servo IDs, naming, manifests |
| `profiles/` | Hardware profiles, one YAML per layout |
| `robots/` | Robot manifests: which module instances make up a physical robot |
| `taskpacks/` | One folder per task pack |
| `hardware/` | Printable tools and fixtures that are not part of the upstream arm |
| `scripts/` | `manifest_to_lerobot.py` turns a robot manifest into LeRobot commands |

## Start here

1. Read `docs/build-plan-step1.md` and order the parts (about $230 for a leader and follower arm, plus cameras and filament).
2. Print the arms while the parts ship.
3. Copy `robots/tabletop-01.example.yaml`, fill in your ports, and generate commands:

```bash
python scripts/manifest_to_lerobot.py robots/tabletop-01.yaml teleoperate
```

4. Record 50 episodes of stage A in `taskpacks/laundry-sort/`, train, run, and append your result to `eval.md`.

## Status

Nothing has been built yet. The interface spec is a proposal; section 9 lists what the first build must answer.

## License

MIT for everything in this repository (code, documents and hardware files). Upstream designs keep their own licenses.
