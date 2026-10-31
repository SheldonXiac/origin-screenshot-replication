from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _rgb_histogram(rgb):
    # A small quantized histogram is useful for choosing a trace color.
    from collections import Counter

    q = rgb.resize((min(240, rgb.width), min(240, rgb.height)))
    pixels = []
    for r, g, b in q.getdata():
        if min(r, g, b) > 245 or max(r, g, b) - min(r, g, b) < 12:
            continue
        pixels.append((r // 16 * 16, g // 16 * 16, b // 16 * 16))
    return [{"rgb": list(c), "count": n} for c, n in Counter(pixels).most_common(12)]


def _lines(path: Path):
    try:
        import cv2
        import numpy as np

        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            return []
        edges = cv2.Canny(image, 50, 150)
        found = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=max(20, min(image.shape) // 12), minLineLength=max(30, min(image.shape) // 5), maxLineGap=8)
        result = []
        for line in (found[:, 0] if found is not None else []):
            x1, y1, x2, y2 = map(int, line)
            dx, dy = abs(x2 - x1), abs(y2 - y1)
            if dx >= 4 * max(dy, 1):
                result.append({"orientation": "horizontal", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "length": dx})
            elif dy >= 4 * max(dx, 1):
                result.append({"orientation": "vertical", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "length": dy})
        return sorted(result, key=lambda x: x["length"], reverse=True)[:20]
    except Exception:
        # Dependency-free fallback: long dark rows/columns are often axes.
        try:
            from PIL import Image
            import numpy as np

            gray = np.asarray(Image.open(path).convert("L"))
            dark = gray < 90
            output = []
            for y, score in enumerate(dark.mean(axis=1)):
                if score >= 0.45:
                    output.append({"orientation": "horizontal", "x1": 0, "y1": y, "x2": gray.shape[1] - 1, "y2": y, "length": gray.shape[1]})
            for x, score in enumerate(dark.mean(axis=0)):
                if score >= 0.45:
                    output.append({"orientation": "vertical", "x1": x, "y1": 0, "x2": x, "y2": gray.shape[0] - 1, "length": gray.shape[0]})
            return output[:20]
        except Exception:
            return []


def _ocr(path: Path):
    try:
        import pytesseract
        from PIL import Image

        data = pytesseract.image_to_data(Image.open(path), output_type=pytesseract.Output.DICT)
        return [
            {"text": t, "confidence": float(c), "left": int(x), "top": int(y), "width": int(w), "height": int(h)}
            for t, c, x, y, w, h in zip(data["text"], data["conf"], data["left"], data["top"], data["width"], data["height"])
            if t.strip() and float(c) >= 0
        ]
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser(description="Inspect a graph screenshot before Origin digitization.")
    ap.add_argument("image", type=Path)
    ap.add_argument("--out", type=Path, default=Path("screenshot_analysis.json"))
    args = ap.parse_args()
    from PIL import Image

    image = Image.open(args.image).convert("RGB")
    raw = args.image.read_bytes()
    result = {
        "image": str(args.image.resolve()),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "width": image.width,
        "height": image.height,
        "dominant_trace_colors": _rgb_histogram(image),
        "axis_like_lines": _lines(args.image),
        "ocr": _ocr(args.image),
        "notes": ["Candidate geometry is diagnostic; confirm plot bounds and axis anchors manually."]
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
