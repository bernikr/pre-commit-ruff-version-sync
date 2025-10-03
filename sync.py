import sys
import tomllib
from pathlib import Path


def main() -> None:
    wd = Path.cwd()
    lock_file = wd / "uv.lock"
    pre_commit_file = wd / ".pre-commit-config.yaml"

    if not lock_file.exists() or not pre_commit_file.exists():
        print("uv.lock or .pre-commit-config.yaml not found in the current directory.")
        sys.exit(0)

    lock = tomllib.loads(lock_file.read_text(encoding="utf-8"))
    ruff_versions = [p["version"] for p in lock["package"] if p["name"] == "ruff"]
    if not ruff_versions:
        print("No ruff version found in uv.lock.")
        sys.exit(0)
    if len(ruff_versions) > 1:
        print("Could not determine a unique ruff version from uv.lock.")
        sys.exit(1)
    lock_ruff_version = ruff_versions[0]
    print(f"Detected uv.lock ruff version: {lock_ruff_version}")
