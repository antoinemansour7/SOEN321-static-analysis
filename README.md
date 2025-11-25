## SOEN321 Static Analysis Toolkit

This repository captures the privacy/permission analysis of Montreal mobility apps.  
The `dataset.py` helper recreates the spreadsheet, emits a styled HTML table, and
generates supporting visualizations for reports.

### Prerequisites

- Python 3.10+ (developed with 3.12)
- pip
- Dependencies:
  ```bash
   python -m pip install pandas openpyxl matplotlib numpy
  ```

### Reproducing the deliverables

1. **Clone / enter the workspace**
   ```bash
   git clone https://github.com/antoinemansour7/SOEN321-static-analysis.git
   cd SOEN321-static-analysis
   ```
2. **Run the helper script (default outputs)**
   ```bash
   python dataset.py
   ```
   This reads `SOEN321_static_analysis.xlsx` and produces:
   - `SOEN321_static_analysis.html` — styled table for quick viewing
   - `SOEN321_static_analysis.xlsx` — regenerated workbook (optional overwrite)
   - `plots/` — PNG charts summarizing trackers, permissions, and risk metrics

### Customizing outputs

Use the CLI flags to control sources/targets:

```bash
python dataset.py \
  --excel-in SOEN321_static_analysis.xlsx \
  --html-out reports/summary.html \
  --excel-out reports/clean_copy.xlsx \
  --plots-dir reports/figures
```

Skip specific artifacts with `--skip-html`, `--skip-excel`, or `--skip-plots`.
Run `python dataset.py --help` for the full option list.

- ### Viewing results
-
- - Open `SOEN321_static_analysis.html` locally (double-click or `start` on Windows) for the color-coded table. 
- - For readers of the report: point them to <https://github.com/antoinemansour7/SOEN321-static-analysis>, then have them follow the GitHub Pages link (or click `SOEN321_static_analysis.html` in the file list) so the styled dashboard opens directly in their browser—no setup needed.
- - Include the PNGs under `plots/` directly in reports/presentations.
- - The Excel workbook remains the canonical data source; update it and rerun the script to refresh all assets.
-
### Repo contents

- `dataset.py` — data ingestion, styling, and plotting pipeline
- `SOEN321_static_analysis.xlsx` — analyzed dataset
- `SOEN321_static_analysis.html` — latest rendered table
- `plots/` — generated visualizations

