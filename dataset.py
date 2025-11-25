"""Utility script for recreating the SOEN321 static analysis sheet with pandas."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


YES_NO_COLUMNS = [
    "Uses_Precise_Location",
    "Uses_Background_Location",
    "Uses_Camera",
    "Uses_Contacts",
    "Uses_Phone_State",
    "Uses_Storage",
    "Uses_System_Alert_Window",
]

GRADIENT_COLUMNS = [
    "Nb_Trackers",
    "Nb_Permissions",
    "Nb_Dangerous_Permissions",
    "Permission_Risk_Score_0to5",
    "Tracker_Intensity_Score_0to5",
    "Transparency_Score_0to5",
    "Retention_Clarity_Score_0to5",
]

SCORE_COLUMNS = [
    "Permission_Risk_Score_0to5",
    "Tracker_Intensity_Score_0to5",
    "Transparency_Score_0to5",
    "Retention_Clarity_Score_0to5",
]


def available_columns(df: pd.DataFrame, columns: List[str]) -> List[str]:
    """Return only the columns that are present in the DataFrame."""
    return [column for column in columns if column in df.columns]


def yes_no_series(series: pd.Series) -> pd.Series:
    """Normalize Yes/No string columns to boolean True/False values."""
    return series.astype(str).str.strip().str.lower().eq("yes")


def build_dataframe(excel_source: Path) -> pd.DataFrame:
    """Create the pandas DataFrame by loading the Excel sheet."""
    try:
        return pd.read_excel(excel_source)
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise SystemExit(
            "Reading .xlsx files requires the optional dependency 'openpyxl'. "
            "Install it with `python -m pip install openpyxl` and re-run this script."
        ) from exc


def yes_no_colors(val: str) -> str:
    """Return CSS background colors for Yes/No cells."""
    if val == "Yes":
        return "background-color:#b7f4c7"
    if val == "No":
        return "background-color:#ffd6cf"
    return ""


def style_dataframe(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Return a styled DataFrame with gradients and Yes/No highlighting."""
    styler = (
        df.style.set_caption("Mobility Apps - Tracker & Permission Overview")
        .format(na_rep="-")
        .set_properties(**{"text-align": "center", "border": "1px solid #ccc", "padding": "6px"})
        .set_table_styles(
            (
                {
                    "selector": "caption",
                    "props": (
                        ("caption-side", "top"),
                        ("font-size", "16px"),
                        ("font-weight", "bold"),
                        ("padding", "8px"),
                    ),
                },
            )
        )
        .background_gradient(subset=available_columns(df, GRADIENT_COLUMNS), cmap="OrRd")
    )

    for column in available_columns(df, YES_NO_COLUMNS):
        styler = styler.map(yes_no_colors, subset=[column])

    return styler


def save_html(styled: pd.io.formats.style.Styler, destination: Path) -> None:
    """Persist the styled DataFrame to an HTML file."""
    destination.write_text(styled.to_html(), encoding="utf-8")


def save_excel(df: pd.DataFrame, destination: Path) -> None:
    """Persist the plain DataFrame to Excel for sharing."""
    df.to_excel(destination, index=False)


def plot_trackers_by_app(df: pd.DataFrame, destination: Path) -> Path | None:
    if "Nb_Trackers" not in df.columns:
        return None

    ordered = df.sort_values("Nb_Trackers", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(ordered["App_Name"], ordered["Nb_Trackers"], color="#1f77b4")
    ax.set_xlabel("Number of embedded trackers")
    ax.set_ylabel("Application")
    ax.set_title("Tracker count per mobility app")
    ax.grid(axis="x", alpha=0.2, linestyle="--")
    fig.tight_layout()
    fig.savefig(destination, dpi=300)
    plt.close(fig)
    return destination


def plot_permission_totals(df: pd.DataFrame, destination: Path) -> Path | None:
    needed = available_columns(df, ["Nb_Permissions", "Nb_Dangerous_Permissions"])
    if len(needed) < 2:
        return None

    x = np.arange(len(df))
    width = 0.4
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width / 2, df["Nb_Permissions"], width=width, label="Total permissions", color="#aec7e8")
    ax.bar(
        x + width / 2,
        df["Nb_Dangerous_Permissions"],
        width=width,
        label="Dangerous permissions",
        color="#ff9896",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(df["App_Name"], rotation=45, ha="right")
    ax.set_ylabel("Count")
    ax.set_title("Declared permissions vs dangerous subset")
    ax.legend()
    ax.grid(axis="y", alpha=0.2, linestyle="--")
    fig.tight_layout()
    fig.savefig(destination, dpi=300)
    plt.close(fig)
    return destination


def plot_average_scores(df: pd.DataFrame, destination: Path) -> Path | None:
    cols = available_columns(df, SCORE_COLUMNS)
    if not cols:
        return None

    means = df[cols].mean().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(means.index, means.values, color="#c5b0d5")
    ax.set_xlabel("Average score (0-5)")
    ax.set_title("Average privacy/transparency scores across apps")
    ax.set_xlim(0, 5)
    for i, value in enumerate(means.values):
        ax.text(value + 0.05, i, f"{value:.1f}", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(destination, dpi=300)
    plt.close(fig)
    return destination


def plot_permission_usage(df: pd.DataFrame, destination: Path) -> Path | None:
    cols = available_columns(df, YES_NO_COLUMNS)
    if not cols:
        return None

    yes_counts = [yes_no_series(df[col]).sum() for col in cols]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(cols, yes_counts, color="#98df8a")
    ax.set_ylabel("Number of apps requesting permission")
    ax.set_title("Prevalence of sensitive permissions across apps")
    ax.set_ylim(0, len(df) + 1)
    ax.set_xticklabels(cols, rotation=45, ha="right")
    for idx, count in enumerate(yes_counts):
        ax.text(idx, count + 0.1, str(count), ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(destination, dpi=300)
    plt.close(fig)
    return destination


def plot_category_scores(df: pd.DataFrame, destination: Path) -> Path | None:
    if "Category" not in df.columns:
        return None

    cols = available_columns(df, SCORE_COLUMNS)
    if not cols:
        return None

    grouped = df.groupby("Category")[cols].median().sort_values(by=cols[0], ascending=False)

    x = np.arange(len(grouped.index))
    width = 0.15
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, col in enumerate(cols):
        offset = (i - (len(cols) - 1) / 2) * width
        ax.bar(
            x + offset,
            grouped[col],
            width=width,
            label=col.replace("_0to5", "").replace("_", " "),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(grouped.index, rotation=20, ha="right")
    ax.set_ylabel("Median score (0-5 scale)")
    ax.set_title("Median risk/transparency scores by category")
    ax.set_ylim(0, 5)
    ax.legend()
    ax.grid(axis="y", alpha=0.2, linestyle="--")

    fig.tight_layout()
    fig.savefig(destination, dpi=300)
    plt.close(fig)
    return destination


def create_plots(df: pd.DataFrame, output_dir: Path) -> List[Path]:
    """Generate a suite of plots that summarize the sheet."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: List[Path | None] = [
        plot_trackers_by_app(df, output_dir / "trackers_by_app.png"),
        plot_permission_totals(df, output_dir / "permissions_vs_dangerous.png"),
        plot_average_scores(df, output_dir / "average_scores.png"),
        plot_permission_usage(df, output_dir / "permission_usage.png"),
        plot_category_scores(df, output_dir / "category_scores.png"),
    ]
    return [path for path in generated if path is not None]


def parse_args(argv: Iterable[str] | None = None):
    """CLI parser that lets you control the output files."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--excel-in",
        type=Path,
        default=Path("SOEN321_static_analysis.xlsx"),
        help="Path to the source Excel workbook to load.",
    )
    parser.add_argument(
        "--html-out",
        type=Path,
        default=Path("SOEN321_static_analysis.html"),
        help="Where to write the styled HTML summary.",
    )
    parser.add_argument(
        "--excel-out",
        type=Path,
        default=Path("SOEN321_static_analysis.xlsx"),
        help="Where to write the (optionally reformatted) Excel file.",
    )
    parser.add_argument(
        "--plots-dir",
        type=Path,
        default=Path("plots"),
        help="Directory in which to store generated PNG visualizations.",
    )
    parser.add_argument("--skip-html", action="store_true", help="Skip generating HTML output.")
    parser.add_argument("--skip-excel", action="store_true", help="Skip generating Excel output.")
    parser.add_argument("--skip-plots", action="store_true", help="Skip generating PNG plots.")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    df = build_dataframe(args.excel_in)
    styled = style_dataframe(df)

    if not args.skip_html:
        save_html(styled, args.html_out)
        print(f"Wrote styled HTML table to {args.html_out.resolve()}")

    if not args.skip_excel:
        save_excel(df, args.excel_out)
        print(f"Wrote DataFrame to Excel at {args.excel_out.resolve()}")

    if not args.skip_plots:
        generated = create_plots(df, args.plots_dir)
        if generated:
            for path in generated:
                print(f"Saved plot -> {path.resolve()}")
        else:
            print("Skipped plot generation because required columns were missing.")

    if args.skip_html and args.skip_excel and args.skip_plots:
        print("No output requested; use --html-out/--excel-out/--plots-dir to persist results.")


if __name__ == "__main__":
    main()
