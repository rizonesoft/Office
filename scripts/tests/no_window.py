# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The creation flag every process a test starts carries (owner, 2026-11-12).

A console program started by a parent that has no console gets a console window of its own, so a test run started
from a windowless parent opened a window for each `pwsh`, `taskkill`, `git` or `python` it started, over whatever
the owner was doing. With CREATE_NO_WINDOW the child gets a console nobody sees, which its own children inherit.
Used by `test_start_campaign.py`, the launcher tests, which start `pwsh` and `taskkill` many times; one of its
tests refuses a start in that file without it.
"""

import subprocess
import sys

NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
