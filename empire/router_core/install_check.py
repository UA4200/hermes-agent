#!/usr/bin/env python3
"""Reusable installer/health-check for router_core.

Not a package installer (router_core has zero required third-party
dependencies -- stdlib only, by design, so it drops into any Python 3.10+
project without a pip install step). This script verifies:
  1. router_core imports cleanly.
  2. Its own test suite passes.
  3. Optional dependencies (gptcache, llmlingua) are detected and reported,
     not required.

Exit code 0 means "safe to import router_core"; non-zero means something
is actually broken, not just "an optional extra is missing".
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROUTER_CORE_DIR = Path(__file__).resolve().parent


def check_import() -> bool:
    try:
        sys.path.insert(0, str(ROUTER_CORE_DIR.parent))
        import router_core  # noqa: F401
        print("[OK] router_core imports cleanly")
        return True
    except Exception as e:
        print(f"[FAIL] router_core failed to import: {e}")
        return False


def check_python_version() -> bool:
    if sys.version_info >= (3, 10):
        print(f"[OK] Python {sys.version.split()[0]} >= 3.10")
        return True
    print(f"[FAIL] Python {sys.version.split()[0]} < 3.10 (router_core uses "
          f"match/PEP 604 union syntax)")
    return False


def check_tests() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(ROUTER_CORE_DIR / "tests"),
         "-q", "-o", "addopts="],
        capture_output=True, text=True,
    )
    ok = result.returncode == 0
    print(f"[{'OK' if ok else 'FAIL'}] test suite: "
          f"{result.stdout.strip().splitlines()[-1] if result.stdout.strip() else result.stderr[-200:]}")
    return ok


def check_optional_deps() -> None:
    for name in ("gptcache", "llmlingua"):
        try:
            __import__(name)
            print(f"[INFO] optional dependency '{name}' is installed "
                  f"(real semantic cache/compression can be wired in)")
        except ImportError:
            print(f"[INFO] optional dependency '{name}' not installed "
                  f"(router_core falls back to no-op — this is fine, not an error)")


def main() -> int:
    print("router_core install check")
    print("=" * 40)
    checks = [check_python_version(), check_import(), check_tests()]
    check_optional_deps()
    print("=" * 40)
    if all(checks):
        print("PASS — router_core is importable and its test suite is green.")
        return 0
    print("FAIL — see [FAIL] lines above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
