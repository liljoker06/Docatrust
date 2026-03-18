from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass(frozen=True)
class OcrItem:
    box: np.ndarray  # shape: (4, 2)
    text: str
    score: Optional[float] = None


def init_paddleocr(lang: str = "fr") -> Any:
    """
    Initialize PaddleOCR with a robust API-compat fallback.

    Returns the PaddleOCR instance, or raises if PaddleOCR is not installed.
    """

    import os

    # Avoid connectivity checks to model hosters (as in notebook).
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

    try:
        from paddleocr import PaddleOCR  # type: ignore
    except Exception as e:
        raise SystemExit(
            "PaddleOCR n'est pas installé dans ce Python.\n"
            "Installe-le (dans le même environnement que celui qui lance le script) :\n"
            "  python3 -m pip install paddleocr\n"
            "\n"
            "Si besoin (CPU) :\n"
            "  python3 -m pip install paddlepaddle\n"
        ) from e

    try:
        return PaddleOCR(use_textline_orientation=True, lang=lang)
    except TypeError:
        # Older variants use `use_angle_cls`.
        return PaddleOCR(use_angle_cls=True, lang=lang)


def paddle_result_to_text(result: Any) -> str:
    """Extract readable text from `paddle_ocr.predict()` output across versions."""
    if not result:
        return "(vide)"

    parts: List[str] = []
    r0 = result[0] if isinstance(result, (list, tuple)) else result

    if isinstance(r0, dict):
        rec = r0.get("rec_texts", r0.get("text", []))
        if isinstance(rec, list):
            for item in rec:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, (list, tuple)):
                    parts.extend([str(x) for x in item if x])
    elif isinstance(r0, (list, tuple)):
        for line in r0:
            if isinstance(line, (list, tuple)) and len(line) >= 2:
                text_part = line[1]
                if isinstance(text_part, (list, tuple)):
                    parts.append(str(text_part[0]))
                else:
                    parts.append(str(text_part))
            elif isinstance(line, str):
                parts.append(line)

    if not parts:
        return "(vide)"

    # If mostly single-character tokens, join in one line.
    if sum(1 for p in parts if len(p) <= 1) > len(parts) / 2:
        return " ".join(parts)

    return "\n".join(parts)


def paddle_predict_to_items(result: Any) -> List[OcrItem]:
    """Return items {box,text,score} from PaddleOCR predict() output."""
    if not result:
        return []

    r0 = result[0] if isinstance(result, (list, tuple)) else result

    # Dict format (some v3 pipelines)
    if isinstance(r0, dict):
        texts = r0.get("rec_texts") or r0.get("texts") or r0.get("text") or []
        scores = r0.get("rec_scores") or r0.get("scores") or []
        boxes = (
            r0.get("dt_polys")
            or r0.get("dt_boxes")
            or r0.get("boxes")
            or r0.get("polys")
            or []
        )
        n = min(len(texts), len(boxes)) if texts and boxes else 0
        out: List[OcrItem] = []
        for i in range(n):
            out.append(
                OcrItem(
                    box=np.array(boxes[i]),
                    text=str(texts[i]),
                    score=float(scores[i]) if i < len(scores) and scores[i] is not None else None,
                )
            )
        return out

    # List/tuple format: [box, (text, score)]
    if isinstance(r0, (list, tuple)):
        out: List[OcrItem] = []
        for det in r0:
            if isinstance(det, (list, tuple)) and len(det) >= 2:
                box = np.array(det[0])
                rec = det[1]
                if isinstance(rec, (list, tuple)) and len(rec) >= 1:
                    text = rec[0]
                    score = rec[1] if len(rec) >= 2 else None
                else:
                    text = rec
                    score = None
                out.append(
                    OcrItem(
                        box=box,
                        text=str(text),
                        score=float(score) if score is not None else None,
                    )
                )
        return out

    return []

