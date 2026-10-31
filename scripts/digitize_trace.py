from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _parse_pair(value: str):
    a, b = value.split(",", 1)
    return float(a), float(b)


def main():
    ap = argparse.ArgumentParser(description="Extract one colored trace and calibrate pixels to XY values.")
    ap.add_argument("image", type=Path)
    ap.add_argument("--roi", required=True, help="left,top,right,bottom in image pixels")
    ap.add_argument("--x-min", type=float, required=True)
    ap.add_argument("--x-max", type=float, required=True)
    ap.add_argument("--y-min", type=float, required=True)
    ap.add_argument("--y-max", type=float, required=True)
    ap.add_argument("--rgb", required=True, help="trace color, e.g. 31,119,180")
    ap.add_argument("--tolerance", type=float, default=70)
    ap.add_argument("--x-scale", choices=["linear", "log10"], default="linear")
    ap.add_argument("--y-scale", choices=["linear", "log10"], default="linear")
    ap.add_argument("--out", type=Path, default=Path("digitized_trace.csv"))
    args = ap.parse_args()
    import numpy as np
    from PIL import Image

    left, top, right, bottom = map(int, args.roi.split(","))
    tr, tg, tb = map(float, args.rgb.split(","))
    image = np.asarray(Image.open(args.image).convert("RGB"), dtype=np.float32)
    crop = image[top:bottom, left:right]
    distance = np.sqrt(((crop - np.array([tr, tg, tb])) ** 2).sum(axis=2))
    mask = distance <= args.tolerance
    rows = []
    for col in range(mask.shape[1]):
        ys = np.flatnonzero(mask[:, col])
        if len(ys) == 0:
            continue
        py = float(np.median(ys)) + top
        px = float(col + left)
        xn = (px - left) / max(right - left - 1, 1)
        yn = (py - top) / max(bottom - top - 1, 1)
        if args.x_scale == "log10":
            import math
            x = 10 ** (math.log10(args.x_min) + xn * (math.log10(args.x_max) - math.log10(args.x_min)))
        else:
            x = args.x_min + xn * (args.x_max - args.x_min)
        if args.y_scale == "log10":
            import math
            y = 10 ** (math.log10(args.y_max) - yn * (math.log10(args.y_max) - math.log10(args.y_min)))
        else:
            y = args.y_max - yn * (args.y_max - args.y_min)
        rows.append((x, y, px, py))
    with args.out.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["X", "Y", "pixel_x", "pixel_y"])
        writer.writerows(rows)
    print(f"wrote {len(rows)} points to {args.out}")


if __name__ == "__main__":
    main()
