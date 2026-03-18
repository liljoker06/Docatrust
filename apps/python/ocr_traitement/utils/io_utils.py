from __future__ import annotations

from pathlib import Path
from typing import List, Optional


def list_facture_images(folder: Path, pattern: Optional[str] = None) -> List[Path]:
    """List invoice images (jpg/png/webp) in a directory."""
    p = Path(folder)
    if not p.exists():
        return []

    files: List[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        files.extend(sorted(p.glob(ext)))

    if pattern:
        low = pattern.lower()
        files = [f for f in files if low in f.name.lower()]

    return files

