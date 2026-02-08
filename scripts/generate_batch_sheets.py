#!/usr/bin/env python3
"""
NAU Concrete Canoe 2026 - Batch Sheet Generator
Generates printable batch sheets for 5-gallon bucket batches.
VPS-compatible: creates text/HTML output; PDF via reportlab if installed.
"""

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "reports" / "batch_sheets"


def calculate_batch_quantities(
    cement_lbs: float,
    sand_lbs: float,
    coarse_agg_lbs: float,
    water_lbs: float,
    batch_scale: float = 1.0,
) -> dict:
    """Scale mix design to batch quantities."""
    return {
        "cement_lbs": round(cement_lbs * batch_scale, 2),
        "sand_lbs": round(sand_lbs * batch_scale, 2),
        "coarse_agg_lbs": round(coarse_agg_lbs * batch_scale, 2),
        "water_lbs": round(water_lbs * batch_scale, 2),
        "admixtures": "Per mix design sheet",
    }


def generate_batch_sheet_text(
    batch_number: int,
    date: str,
    quantities: dict,
) -> str:
    """Generate plain-text batch sheet (always works, no deps)."""
    return f"""
================================================================================
NAU CONCRETE CANOE 2026 - BATCH SHEET
================================================================================
Batch #: {batch_number}          Date: {date}
Mixer Name: _________________    QC: _________________

COMPONENT CHECKLIST (target weights)
--------------------------------------------------------------------------------
  [ ] Cement:        {quantities['cement_lbs']:.2f} lbs
  [ ] Sand:          {quantities['sand_lbs']:.2f} lbs
  [ ] Coarse agg:    {quantities['coarse_agg_lbs']:.2f} lbs
  [ ] Water:         {quantities['water_lbs']:.2f} lbs
  [ ] Admixtures:    {quantities['admixtures']}

QUALITY CONTROL
--------------------------------------------------------------------------------
  [ ] Slump: _____ in    [ ] Temperature: _____ °F
  [ ] Visual inspection OK
  [ ] Mix time: _____ min

Notes:
________________________________________________________________________________
________________________________________________________________________________
________________________________________________________________________________

================================================================================
"""


def save_batch_sheet(batch_number: int, content: str) -> Path:
    """Save batch sheet to file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    out_path = OUTPUT_DIR / f"batch_sheet_{date_str}_{batch_number:03d}.txt"
    with open(out_path, "w") as f:
        f.write(content)
    return out_path


def main() -> int:
    # Example mix (1 yd³ scaled to ~0.05 yd³ = ~5 gal batch)
    # User should update from Miles' mix design
    FULL_BATCH = {
        "cement_lbs": 25.0,
        "sand_lbs": 35.0,
        "coarse_agg_lbs": 20.0,
        "water_lbs": 12.0,
    }
    BATCH_SCALE = 0.05  # 5-gallon bucket ≈ 5% of 1 yd³

    quantities = calculate_batch_quantities(
        cement_lbs=FULL_BATCH["cement_lbs"],
        sand_lbs=FULL_BATCH["sand_lbs"],
        coarse_agg_lbs=FULL_BATCH["coarse_agg_lbs"],
        water_lbs=FULL_BATCH["water_lbs"],
        batch_scale=BATCH_SCALE,
    )

    batch_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    date = datetime.now().strftime("%Y-%m-%d")
    content = generate_batch_sheet_text(batch_num, date, quantities)

    out_path = save_batch_sheet(batch_num, content)
    print(f"Batch sheet saved: {out_path}")
    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
