from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class LayoutZones:
    header: Tuple[int, int]
    table: Tuple[int, int]
    total: Tuple[int, int]

    def crop_header(self, img_bgr: np.ndarray) -> np.ndarray:
        return img_bgr[self.header[0] : self.header[1], :]

    def crop_table(self, img_bgr: np.ndarray) -> np.ndarray:
        return img_bgr[self.table[0] : self.table[1], :]

    def crop_total(self, img_bgr: np.ndarray) -> np.ndarray:
        return img_bgr[self.total[0] : self.total[1], :]


def default_zones(h: int) -> LayoutZones:
    """
    Notebook heuristic:
    - header: 0% -> 25% (used for OCR blocks)
    - table: 25% -> 75%
    - total: 75% -> 100%
    """

    return LayoutZones(
        header=(0, int(0.25 * h)),
        table=(int(0.25 * h), int(0.75 * h)),
        total=(int(0.75 * h), h),
    )

