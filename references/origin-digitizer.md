# Origin Enhanced Digitizer route

OriginLab's documented workflow is: select **Digitize Image**, import the image, remove Cartesian gridlines or background noise when needed, press **Edit Axes**, align four reference lines to known axis locations and enter their values, then capture points with **Manually Pick Points**, **Auto Trace Line By Points**, **Auto Pick Points By Grids**, or **Area Auto Trace**. Save axis settings when similar images will be processed. The official tutorial is:

<https://docs.originlab.com/tutorials/enhanced-digitizer/>

Use the native digitizer when the screenshot has no source table or when a trace is easier to select interactively. Export the digitized points to a worksheet and use that worksheet as the input to the Origin graph. For a log axis, select the log scale and calibrate with tick values in the log domain; do not linearly map pixel distance to the displayed labels.

For automated extraction, the companion Python script retains pixel coordinates and the calibration rectangle. It is a reproducible aid, not a replacement for checking axis anchors and ambiguous crossings by eye.
