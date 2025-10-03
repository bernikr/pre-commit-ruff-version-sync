import sys
import tomllib
from pathlib import Path

import yaml


def main() -> None:
    wd = Path.cwd()
    lock_file = wd / "uv.lock"
    pre_commit_file = wd / ".pre-commit-config.yaml"

    if not lock_file.exists() or not pre_commit_file.exists():
        print("uv.lock or .pre-commit-config.yaml not found in the current directory.")
        sys.exit(1)

    lock = tomllib.loads(lock_file.read_text(encoding="utf-8"))
    ruff_versions = [p["version"] for p in lock["package"] if p["name"] == "ruff"]
    if not ruff_versions:
        print("No ruff version found in uv.lock.")
        sys.exit(1)
    if len(ruff_versions) > 1:
        print("Could not determine a unique ruff version from uv.lock.")
        sys.exit(1)
    lock_ruff_version = ruff_versions[0]
    print(f"Detected uv.lock ruff version: {lock_ruff_version}")

    pc_content = pre_commit_file.read_text(encoding="utf-8")
    pc = yaml.safe_load(pc_content)
    ruff_versions = [
        repo["rev"] for repo in pc["repos"] if repo["repo"] == "https://github.com/astral-sh/ruff-pre-commit"
    ]
    if not ruff_versions:
        print("No ruff version found in .pre-commit-config.yaml.")
        sys.exit(1)
    if len(ruff_versions) > 1:
        print("Could not determine a unique ruff version from .pre-commit-config.yaml.")
        sys.exit(1)
    pc_ruff_version = ruff_versions[0].removeprefix("v")
    print(f"Detected pre-commit ruff version: {pc_ruff_version}")

    if lock_ruff_version == pc_ruff_version:
        print("Versions are already in sync.")
        sys.exit(0)

    pc_content_new = pc_content.replace(
        f"repo: https://github.com/astral-sh/ruff-pre-commit\n    rev: v{pc_ruff_version}",
        f"repo: https://github.com/astral-sh/ruff-pre-commit\n    rev: v{lock_ruff_version}",
    )

    if pc_content == pc_content_new:
        print("Cant replace version in .pre-commit-config.yaml. Please do so manually.")
        sys.exit(1)

    print(f"Updating .pre-commit-config.yaml ruff version to {lock_ruff_version}")
    pre_commit_file.write_text(pc_content_new, encoding="utf-8")
