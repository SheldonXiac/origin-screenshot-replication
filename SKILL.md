---
name: origin-screenshot-replication
description: Reconstruct a scientific graph from a screenshot in editable Origin/OriginPro. Use when the user provides an image and wants its data read, the Origin workflow explained, and a native Origin project plus matching exports produced with Python-assisted digitization and visual QA.
metadata:
  category: scientific-plotting
  homepage: https://docs.originlab.com/tutorials/enhanced-digitizer/
---

# Origin screenshot replication

Use this skill together with `originplot` and `python-origin-plotting` when they are installed. The goal is a worksheet-backed, editable Origin project; a Python or raster preview is only a diagnostic.

## Workflow

1. Preserve the supplied image and record its SHA-256. Run `scripts/analyze_screenshot.py` to report dimensions, candidate plot bounds, OCR text (when Tesseract is available), long axis-like lines, and dominant trace colors.
2. Separate what is observed from what is inferred. Read visible titles, tick labels, legends, markers, line styles, panels, and annotations. Mark missing axis values, hidden data, and ambiguous series as `uncertain`; ask for the source table or axis anchors when exact recovery is required.
3. Calibrate pixels to data coordinates. Prefer four known axis anchors and a linear/log decision supported by tick labels. For image-only data, use `scripts/digitize_trace.py` with an explicit ROI and color; keep the generated CSV labelled `digitized_approximate` and retain pixel coordinates and calibration metadata.
4. Explain the native Origin route before execution. For ordinary images use Origin's Enhanced Digitizer: import image, remove gridlines/background noise, edit the four axes anchors, then manually pick points or use Auto Trace Line By Points/Area Auto Trace. Export the extracted data to a worksheet. See `references/origin-digitizer.md`.
5. Create a confirmed FigureSpec (data mapping, plot type, scales, panel layout, per-series style, labels, legend, dimensions). Compile an Origin-independent OperationPlan where possible. Builders describe intent; only the Origin adapter calls `originpro`/LabTalk.
6. Execute visibly in Origin/OriginPro. Use `originpro` to create a workbook from the extracted CSV, bind X/Y/error columns, create graph layers, apply native line/marker/axis/legend settings, save `.opju`, and export PNG/TIFF/PDF. Use an ASCII temporary directory for Origin exports if a non-ASCII path fails. Never use the screenshot as a final raster background and never claim an unreadable value was recovered.
7. Reopen the saved `.opju`, read back worksheet bindings and plot count/style, then compare the reopened export with the reference using `scripts/compare_images.py`. Report numeric differences and the remaining uncertainty. A screenshot match alone does not prove editability.

## Decision rules

- Source data is immutable. Do not smooth, fit, normalize, remove outliers, or invent points unless the user explicitly asks.
- Use templates only after inspecting that they contain editable graphs and compatible bindings. A downloaded image, `.otp`, or copied OPJU is not proof of reuse.
- If Origin or `originpro` is unavailable, produce the analysis, calibrated CSV, FigureSpec, and runnable Python script, and say that native execution is pending. Do not fake an Origin result with matplotlib.
- Treat OCR as a label aid, not scientific data recovery. Tick values and series values must be checked against visible anchors or the source table.
- Distinguish `source_exact`, `digitized_approximate`, and `semantic_reconstruction` in every report and output manifest.

## Commands

```powershell
python scripts/analyze_screenshot.py figure.png --out analysis.json
python scripts/digitize_trace.py figure.png --roi 96,62,1112,756 `
  --x-min 0 --x-max 10 --y-min 0 --y-max 100 --rgb 31,119,180 --out trace.csv
python scripts/compare_images.py reference.png reproduced.png --out qa.json --diff diff.png
```

For a table-driven figure, use `$originplot` for FigureSpec/OperationPlan and `$python-origin-plotting` for the live `originpro` implementation. Read their detailed references only for the selected route.

## Local Origin runtime

Discover and verify the user's Origin installation before live execution; do not assume a drive, version, or executable path. Keep the Origin window visible and use a Python environment whose `originpro` architecture matches the Origin installation.
