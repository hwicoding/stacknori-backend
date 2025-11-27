#!/usr/bin/env python3
"""
Simple documentation guard to ensure mandatory sections exist.

Used in CI to catch accidental README regressions.
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## API 개요",
    "## 로드맵/자료 시드 데이터",
    "## 초기 관리자 계정 생성",
]


def main() -> int:
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("README.md not found", file=sys.stderr)
        return 1

    content = readme_path.read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_SECTIONS if section not in content]
    if missing:
        print("README.md is missing required sections:", file=sys.stderr)
        for section in missing:
            print(f"  - {section}", file=sys.stderr)
        return 1

    print("Documentation validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

