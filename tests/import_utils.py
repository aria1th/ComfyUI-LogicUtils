from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path


_PKG_NAME = "comfyui_logicutils"


def ensure_local_package() -> str:
    """Expose the repo's sources as an importable package for unit tests.

    The upstream folder name contains a hyphen, which isn't a valid Python import name.
    We create an in-memory package module (with a __path__) so intra-package relative
    imports like `from .autonode import ...` work normally.
    """
    if _PKG_NAME in sys.modules:
        return _PKG_NAME

    repo_root = Path(__file__).resolve().parents[1]
    package = types.ModuleType(_PKG_NAME)
    package.__path__ = [str(repo_root)]
    sys.modules[_PKG_NAME] = package
    return _PKG_NAME


def import_local(module: str):
    pkg = ensure_local_package()
    return importlib.import_module(f"{pkg}.{module}")

