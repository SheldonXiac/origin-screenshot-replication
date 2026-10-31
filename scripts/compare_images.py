from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Compare a reproduced export with a reference image.")
    ap.add_argument("reference", type=Path)
    ap.add_argument("reproduced", type=Path)
    ap.add_argument("--out", type=Path, default=Path("image_qa.json"))
    ap.add_argument("--diff", type=Path)
    args = ap.parse_args()
    import numpy as np
    from PIL import Image

    ref = Image.open(args.reference).convert("RGB")
    got = Image.open(args.reproduced).convert("RGB").resize(ref.size)
    a, b = np.asarray(ref, dtype=np.float32), np.asarray(got, dtype=np.float32)
    delta = np.abs(a - b)
    result = {"reference": str(args.reference.resolve()), "reproduced": str(args.reproduced.resolve()), "size": list(ref.size), "mae": float(delta.mean()), "rmse": float(np.sqrt(((a - b) ** 2).mean()))}
    try:
        from skimage.metrics import structural_similarity
        result["ssim"] = float(structural_similarity(a, b, channel_axis=2, data_range=255))
    except Exception:
        result["ssim"] = None
    if args.diff:
        Image.fromarray(np.clip(delta * 4, 0, 255).astype("uint8")).save(args.diff)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
