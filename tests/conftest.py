"""Shared pytest configuration for Project P1 tests."""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

# Allow tests to import the package from source even without an editable install.
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
