from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_mcp_sample_payloads_match_live_contracts() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/check-mcp-sample-payloads.py"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
