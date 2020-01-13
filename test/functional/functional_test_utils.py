import os
from pathlib import Path

__all__ = ("vector_file",)

HERE = Path(os.path.abspath(os.path.dirname(__file__)))
VECTORS = HERE / ".." / "vectors"


def vector_file(vector_name: str) -> Path:
    return VECTORS / vector_name
