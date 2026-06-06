"""Project path helpers — keeps data files working regardless of cwd."""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_path(*parts):
    return os.path.join(PROJECT_ROOT, *parts)
