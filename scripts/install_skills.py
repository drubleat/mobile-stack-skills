#!/usr/bin/env python3
"""Copy selected skills into an explicitly chosen agent skills directory."""
import argparse
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("mobile-stack-toolkit", "supabase-postgres-best-practices")


def install(target: Path, names: list[str], root: Path = ROOT) -> list[Path]:
    """Refuse collisions before copying; roll back this invocation on failure."""
    root = root.resolve()
    target = target.expanduser().resolve()
    names = list(dict.fromkeys(names))
    for name in names:
        if name not in SKILLS:
            raise ValueError(f"Unknown skill: {name}")
        source = root / name
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"Missing skill: {source}")
        if source.is_symlink() or any(p.is_symlink() for p in source.rglob("*")):
            raise ValueError(f"Skill contains symlinks: {source}")
        destination = target / name
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"Already exists; review and move it first: {destination}")
        if target == source or source in target.parents:
            raise ValueError("Install target must be outside the source skill")
    target.mkdir(parents=True, exist_ok=True)
    installed = []
    try:
        with tempfile.TemporaryDirectory(prefix=".mobile-skills-", dir=target) as tmp:
            for name in names:
                shutil.copytree(root / name, Path(tmp) / name)
            for name in names:
                destination = target / name
                # mkdir provides a no-clobber claim, including concurrent installers.
                destination.mkdir()
                installed.append(destination)
                for child in (Path(tmp) / name).iterdir():
                    shutil.move(str(child), destination / child.name)
    except Exception:
        for destination in reversed(installed):
            shutil.rmtree(destination)
        raise
    return installed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path,
                        help="e.g. /path/to/project/.agents/skills or ~/.agents/skills")
    parser.add_argument("--skill", action="append", choices=SKILLS,
                        help="Repeat to select skills; default: both")
    args = parser.parse_args()
    try:
        for path in install(args.target, args.skill or list(SKILLS)):
            print(f"Installed {path}")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
