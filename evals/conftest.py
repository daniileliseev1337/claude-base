"""Pytest configuration for ~/.claude/evals/.

Adds skill directories to sys.path so test files can import skill
modules directly (e.g. `from pipeline import smart_cap_height_detect`).
"""
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / ".claude" / "skills"

# Add every skill subdirectory that has Python files to sys.path
for skill_dir in SKILLS_DIR.iterdir():
    if not skill_dir.is_dir():
        continue
    if any(skill_dir.glob("*.py")):
        sys.path.insert(0, str(skill_dir))
