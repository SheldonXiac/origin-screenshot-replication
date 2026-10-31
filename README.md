# Origin Screenshot Replication

将科研图表截图复刻为数据驱动、可编辑的 Origin/OriginPro 工程的 Codex skill。

提供截图分析、彩色曲线近似取数、像素到数据坐标转换、Origin 绘图流程和导出图像对比。目标交付包括 CSV、FigureSpec、OperationPlan、可编辑 OPJU 及 PNG/TIFF/PDF；后三类文件需要实际运行 Origin 后生成，辅助脚本本身不会生成 Origin 工程。

## 安装

将本仓库下载或克隆为 `origin-screenshot-replication` 文件夹，并把整个文件夹复制到 `~/.codex/skills/origin-screenshot-replication`。若目标目录已存在，请先备份并比较版本。重启 Codex 后可调用：

```text
使用 $origin-screenshot-replication 复刻这张图表，标明近似取数，并生成经重开验证的可编辑 Origin 工程。
```

Python 3.9+，基础依赖：

```powershell
python -m pip install -r requirements.txt
```

原生绘图需 Windows、已安装并授权的 Origin/OriginPro，以及匹配的 `originpro` 自动化环境。Origin 软件及许可证不包含在本仓库内。可选依赖为 `opencv-python`（候选轴线检测）、`pytesseract` 与独立安装的 Tesseract（OCR）、`scikit-image`（SSIM）。缺少可选依赖时，对应诊断会回退或返回空值。

可配合 [originplot](https://github.com/peterbruce716-art/originplot-skill) 和 [python-origin-plotting](https://github.com/Gerry2024-hub/Gerry2024-hub-python-origin-plotting-skill)；上游项目独立维护，详见 [integration.md](references/integration.md)。

## 辅助脚本

```powershell
python scripts/analyze_screenshot.py figure.png --out analysis.json
python scripts/digitize_trace.py figure.png --roi 96,62,1112,756 --x-min 0 --x-max 10 --y-min 0 --y-max 100 --rgb 31,119,180 --out digitized_approximate.csv
python scripts/compare_images.py reference.png reproduced.png --out qa.json --diff diff.png
```

`--roi` 为 `left,top,right,bottom`，右边界和下边界不包含在截取范围内。数据锚点对应所截像素范围的两端。对数坐标需显式指定 `--x-scale log10` 或 `--y-scale log10`。

取数脚本按列聚合指定颜色的像素。同色图例、交叉曲线和填充区可能干扰结果，必须检查 ROI、标定与提取结果；它不能恢复被遮挡或不可读的原始数据。输出保留像素坐标，所得数值应标为 `digitized_approximate`。不应把近似数据当作原始实验数据，也不应在未经要求时平滑、拟合或补造点。

图像对比会将导出图缩放至参考图尺寸后计算 MAE/RMSE，并在可用时报告 SSIM。像素相似度只用于视觉诊断；必须重开 OPJU 并核对工作表、曲线绑定和样式，才能确认可编辑性。

完整执行规则见 [SKILL.md](SKILL.md)，原生取数流程见 [Origin Digitizer 说明](references/origin-digitizer.md)。
