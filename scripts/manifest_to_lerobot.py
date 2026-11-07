#!/usr/bin/env python3
"""Turn a robot manifest (robots/*.yaml) into a LeRobot command line.

Usage:
    python scripts/manifest_to_lerobot.py robots/tabletop-01.yaml teleoperate
    python scripts/manifest_to_lerobot.py robots/tabletop-01.yaml record \
        --repo-id you/laundry-sort-stage-a --task "Put the clothing item in the tray" --episodes 50
    python scripts/manifest_to_lerobot.py robots/tabletop-01.yaml rollout \
        --policy you/act-laundry-sort-a --task "Put the clothing item in the tray"
    python scripts/manifest_to_lerobot.py robots/tabletop-01.yaml calibrate
    python scripts/manifest_to_lerobot.py robots/tabletop-01.yaml setup-motors

Prints the command; pipe to `sh` to run it. Needs PyYAML (`pip install pyyaml`).
Flag names follow the LeRobot docs as of November 2026; check them against your installed version.
"""

import argparse
import shlex
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

CAMERA_NAMES = {"top", "front", "wrist", "wrist_left", "wrist_right"}
ARM_MODELS = {"so100_follower", "so101_follower"}
TELEOP_MODELS = {"so100_leader", "so101_leader"}


def load_manifest(path: Path) -> dict:
    with path.open() as f:
        manifest = yaml.safe_load(f)
    if not isinstance(manifest, dict) or "modules" not in manifest:
        raise SystemExit(f"{path}: expected a mapping with a 'modules' list")
    return manifest


def by_type(manifest: dict, kind: str) -> list[dict]:
    return [m for m in manifest["modules"] if m.get("type") == kind]


def validate(manifest: dict) -> None:
    errors = []
    arms = by_type(manifest, "arm")
    if len(arms) != 1:
        errors.append(f"expected exactly one arm module for now, found {len(arms)}")
    for arm in arms:
        if arm.get("model") not in ARM_MODELS:
            errors.append(f"arm model {arm.get('model')!r} not in {sorted(ARM_MODELS)}")
        for key in ("instance", "port"):
            if not arm.get(key):
                errors.append(f"arm module is missing '{key}'")
    for teleop in by_type(manifest, "teleop"):
        if teleop.get("model") not in TELEOP_MODELS:
            errors.append(f"teleop model {teleop.get('model')!r} not in {sorted(TELEOP_MODELS)}")
        for key in ("instance", "port"):
            if not teleop.get(key):
                errors.append(f"teleop module is missing '{key}'")
    seen = set()
    for cam in by_type(manifest, "camera"):
        name = cam.get("name")
        if name not in CAMERA_NAMES:
            errors.append(f"camera name {name!r} not in {sorted(CAMERA_NAMES)}")
        if name in seen:
            errors.append(f"camera name {name!r} used twice")
        seen.add(name)
        if cam.get("port") is None:
            errors.append(f"camera {name!r} is missing 'port'")
    if errors:
        raise SystemExit("manifest errors:\n  " + "\n  ".join(errors))


def camera_arg(cameras: list[dict]) -> str:
    """Build the --robot.cameras value in LeRobot's inline-dict syntax."""
    parts = []
    for cam in cameras:
        port = cam["port"]
        index_or_path = port if isinstance(port, int) else str(port)
        parts.append(
            f"{cam['name']}: {{type: opencv, index_or_path: {index_or_path}, "
            f"width: {cam.get('width', 640)}, height: {cam.get('height', 480)}, "
            f"fps: {cam.get('fps', 30)}}}"
        )
    return "{ " + ", ".join(parts) + " }"


def robot_args(manifest: dict, with_cameras: bool = True) -> list[str]:
    arm = by_type(manifest, "arm")[0]
    args = [
        f"--robot.type={arm['model']}",
        f"--robot.port={arm['port']}",
        f"--robot.id={arm['instance']}",
    ]
    cameras = by_type(manifest, "camera")
    if with_cameras and cameras:
        args.append(f"--robot.cameras={camera_arg(cameras)}")
    return args


def teleop_args(manifest: dict) -> list[str]:
    teleops = by_type(manifest, "teleop")
    if not teleops:
        raise SystemExit("this command needs a teleop module in the manifest")
    t = teleops[0]
    return [
        f"--teleop.type={t['model']}",
        f"--teleop.port={t['port']}",
        f"--teleop.id={t['instance']}",
    ]


def build(manifest: dict, args: argparse.Namespace) -> list[list[str]]:
    """Return one or more commands, each as an argv list."""
    cmd = args.command
    if cmd == "setup-motors":
        arm = by_type(manifest, "arm")[0]
        cmds = [["lerobot-setup-motors", f"--robot.type={arm['model']}", f"--robot.port={arm['port']}"]]
        for t in by_type(manifest, "teleop"):
            cmds.append(["lerobot-setup-motors", f"--teleop.type={t['model']}", f"--teleop.port={t['port']}"])
        return cmds
    if cmd == "calibrate":
        cmds = [["lerobot-calibrate", *robot_args(manifest, with_cameras=False)]]
        for _ in by_type(manifest, "teleop"):
            cmds.append(["lerobot-calibrate", *teleop_args(manifest)])
        return cmds
    if cmd == "teleoperate":
        return [["lerobot-teleoperate", *robot_args(manifest, not args.no_cameras), *teleop_args(manifest),
                 "--display_data=true"]]
    if cmd == "record":
        return [[
            "lerobot-record", *robot_args(manifest), *teleop_args(manifest),
            "--display_data=true",
            f"--dataset.repo_id={args.repo_id}",
            "--dataset.no_stamp=true",
            f"--dataset.num_episodes={args.episodes}",
            f"--dataset.episode_time_s={args.episode_time}",
            f"--dataset.reset_time_s={args.reset_time}",
            f"--dataset.single_task={args.task}",
        ]]
    if cmd == "rollout":
        return [[
            "lerobot-rollout", "--strategy.type=base", f"--policy.path={args.policy}",
            *robot_args(manifest), f"--task={args.task}", f"--duration={args.duration}",
        ]]
    raise SystemExit(f"unknown command {cmd!r}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("manifest", type=Path)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("setup-motors")
    sub.add_parser("calibrate")
    tele = sub.add_parser("teleoperate")
    tele.add_argument("--no-cameras", action="store_true")
    rec = sub.add_parser("record")
    rec.add_argument("--repo-id", required=True, help="Hugging Face dataset id, e.g. you/laundry-sort-stage-a")
    rec.add_argument("--task", required=True, help="task description string")
    rec.add_argument("--episodes", type=int, default=50)
    rec.add_argument("--episode-time", type=int, default=30)
    rec.add_argument("--reset-time", type=int, default=15)
    roll = sub.add_parser("rollout")
    roll.add_argument("--policy", required=True, help="policy path or Hugging Face repo id")
    roll.add_argument("--task", required=True)
    roll.add_argument("--duration", type=int, default=60)
    args = p.parse_args()

    manifest = load_manifest(args.manifest)
    validate(manifest)
    for argv in build(manifest, args):
        print(" ".join(shlex.quote(a) for a in argv))


if __name__ == "__main__":
    main()
