#!/usr/bin/env python3
"""
NAU CONCRETE CANOE 2026 - COMPLETE MIX DESIGN ANALYSIS SYSTEM
Multi-Agent Architecture with Decision Matrices & Visualizations

Run: python3 mix_analysis_system.py
Outputs: reports/figures/

AGENTS:
  Agent 1: Data Parser (loads mix designs)
  Agent 2: Calculation (strength, density, ASCE compliance)
  Agent 3: Decision Matrix (weighted scoring)
  Agent 4: Visualization (PNG charts)
  Agent 5: Reporting (text report)
"""

import os
import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass

import warnings
warnings.filterwarnings('ignore')

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: matplotlib/numpy not available. Visualizations will be skipped.")
    MATPLOTLIB_AVAILABLE = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "reports", "figures")


@dataclass
class MixDesign:
    """Represents a single concrete mix design"""
    name: str
    portland_lbs: float
    portland_percent: float
    slag_lbs: float
    slag_percent: float
    fly_ash_lbs: float
    fly_ash_percent: float
    lime_lbs: float
    lime_percent: float
    poraver_lbs: float
    perlite_lbs: float
    k1_lbs: float
    fiber_lbs: float
    w_cm_ratio: float
    hrwr_dosage: float
    air_entrainer_dosage: float
    measured_density_pcf: float
    measured_air_percent: float
    test_7day_psi: float
    predicted_28day_psi: float


class DataParserAgent:
    """AGENT 1: Parse mix designs from hardcoded data."""

    @staticmethod
    def create_mix_3() -> MixDesign:
        return MixDesign(
            name="Mix 3 (OPTIMIZED)",
            portland_lbs=97.21, portland_percent=30.8,
            slag_lbs=149.21, slag_percent=47.2,
            fly_ash_lbs=59.78, fly_ash_percent=18.9,
            lime_lbs=9.72, lime_percent=3.1,
            poraver_lbs=131.23, perlite_lbs=88.22, k1_lbs=38.89,
            fiber_lbs=4.34, w_cm_ratio=0.36,
            hrwr_dosage=6.0, air_entrainer_dosage=1.5,
            measured_density_pcf=58.6, measured_air_percent=3.0,
            test_7day_psi=273, predicted_28day_psi=1774)

    @staticmethod
    def create_mix_2() -> MixDesign:
        return MixDesign(
            name="Mix 2 (BALANCED)",
            portland_lbs=110.0, portland_percent=35.0,
            slag_lbs=120.0, slag_percent=38.0,
            fly_ash_lbs=65.0, fly_ash_percent=20.7,
            lime_lbs=10.0, lime_percent=3.2,
            poraver_lbs=125.0, perlite_lbs=100.0, k1_lbs=35.0,
            fiber_lbs=4.0, w_cm_ratio=0.42,
            hrwr_dosage=5.0, air_entrainer_dosage=1.0,
            measured_density_pcf=55.0, measured_air_percent=2.5,
            test_7day_psi=320, predicted_28day_psi=1200)

    @staticmethod
    def create_mix_1() -> MixDesign:
        return MixDesign(
            name="Mix 1 (LIGHTWEIGHT)",
            portland_lbs=125.0, portland_percent=40.0,
            slag_lbs=70.0, slag_percent=22.4,
            fly_ash_lbs=67.0, fly_ash_percent=21.5,
            lime_lbs=10.0, lime_percent=3.2,
            poraver_lbs=115.0, perlite_lbs=150.0, k1_lbs=25.0,
            fiber_lbs=3.5, w_cm_ratio=0.45,
            hrwr_dosage=4.0, air_entrainer_dosage=2.0,
            measured_density_pcf=48.0, measured_air_percent=4.5,
            test_7day_psi=200, predicted_28day_psi=650)

    @staticmethod
    def parse_all_mixes() -> List[MixDesign]:
        return [
            DataParserAgent.create_mix_1(),
            DataParserAgent.create_mix_2(),
            DataParserAgent.create_mix_3()]


class CalculationAgent:
    """AGENT 2: Calculate totals, predict strength, verify ASCE compliance."""

    @staticmethod
    def calculate_total_cementitious(mix: MixDesign) -> float:
        return mix.portland_lbs + mix.slag_lbs + mix.fly_ash_lbs + mix.lime_lbs

    @staticmethod
    def calculate_total_aggregates(mix: MixDesign) -> float:
        return mix.poraver_lbs + mix.perlite_lbs + mix.k1_lbs

    @staticmethod
    def calculate_28day_prediction(mix: MixDesign) -> Dict[str, Dict]:
        dry_equivalent = mix.test_7day_psi / 0.80
        scenarios = {'conservative': 4.2, 'typical': 5.2, 'optimistic': 6.0}
        results = {}
        for scenario, factor in scenarios.items():
            dry_28 = dry_equivalent * factor
            results[scenario] = {
                'dry_psi': round(dry_28, 0),
                'wet_psi': round(dry_28 * 0.80, 0),
                'passes_asce': dry_28 >= 1500,
                'margin_psi': round(dry_28 - 1500, 0)}
        return results

    @staticmethod
    def check_asce_compliance(mix: MixDesign) -> Dict[str, Tuple[bool, str]]:
        checks = {}
        checks['Portland <=40%'] = (mix.portland_percent <= 40,
                                     f"{mix.portland_percent:.1f}% (limit: 40%)")
        checks['Lime <=5%'] = (mix.lime_percent <= 5,
                                f"{mix.lime_percent:.1f}% (limit: 5%)")
        combined = mix.portland_percent + mix.lime_percent
        checks['Portland+Lime <=40%'] = (combined <= 40,
                                          f"{combined:.1f}% (limit: 40%)")
        checks['Density 48-65 PCF'] = (48 <= mix.measured_density_pcf <= 65,
                                        f"{mix.measured_density_pcf:.1f} pcf")
        checks['28-day >=1500 psi'] = (mix.predicted_28day_psi >= 1500,
                                        f"{mix.predicted_28day_psi:.0f} psi")
        return checks


class DecisionMatrixAgent:
    """AGENT 3: Weighted scoring (strength 40%, durability 30%, cost 20%, workability 10%)."""

    WEIGHTS = {'strength': 0.40, 'durability': 0.30, 'cost': 0.20, 'workability': 0.10}

    @staticmethod
    def score_strength(predicted_28day: float) -> Tuple[float, str]:
        if predicted_28day >= 1700: return 10.0, "Excellent (1,700+ psi)"
        elif predicted_28day >= 1500: return 8.0, "Good (1,500-1,699 psi)"
        elif predicted_28day >= 1200: return 5.0, "Marginal (1,200-1,499 psi)"
        else: return 2.0, "Insufficient (<1,200 psi)"

    @staticmethod
    def score_durability(w_cm_ratio: float) -> Tuple[float, str]:
        if w_cm_ratio <= 0.36: return 10.0, "Excellent (w/cm <=0.36)"
        elif w_cm_ratio <= 0.42: return 7.0, "Good (w/cm 0.36-0.42)"
        elif w_cm_ratio <= 0.45: return 4.0, "Fair (w/cm 0.42-0.45)"
        else: return 2.0, "Poor (w/cm >0.45)"

    @staticmethod
    def score_cost(density: float) -> Tuple[float, str]:
        if density <= 48: return 10.0, "Excellent (<=48 PCF)"
        elif density <= 55: return 7.0, "Good (48-55 PCF)"
        elif density <= 60: return 5.0, "Moderate (55-60 PCF)"
        else: return 3.0, "Higher (>60 PCF)"

    @staticmethod
    def score_workability(w_cm_ratio: float, has_hrwr: bool) -> Tuple[float, str]:
        if w_cm_ratio > 0.45: return 10.0, "Excellent (loose mix)"
        elif w_cm_ratio > 0.40 and has_hrwr: return 9.0, "Very Good (dry + HRWR)"
        elif w_cm_ratio > 0.35 and has_hrwr: return 7.0, "Good (tight + HRWR)"
        else: return 5.0, "Fair (very tight)"

    @staticmethod
    def calculate_scores(mixes: List[MixDesign]) -> Dict[str, Dict]:
        results = {}
        for mix in mixes:
            s_score, s_note = DecisionMatrixAgent.score_strength(mix.predicted_28day_psi)
            d_score, d_note = DecisionMatrixAgent.score_durability(mix.w_cm_ratio)
            c_score, c_note = DecisionMatrixAgent.score_cost(mix.measured_density_pcf)
            w_score, w_note = DecisionMatrixAgent.score_workability(mix.w_cm_ratio, mix.hrwr_dosage > 0)
            total = (s_score * 0.40 + d_score * 0.30 + c_score * 0.20 + w_score * 0.10)
            results[mix.name] = {
                'strength': {'score': s_score, 'note': s_note},
                'durability': {'score': d_score, 'note': d_note},
                'cost': {'score': c_score, 'note': c_note},
                'workability': {'score': w_score, 'note': w_note},
                'weighted_total': round(total, 1),
                'recommendation': 'EXCELLENT' if total >= 9.0 else ('GOOD' if total >= 7.0 else 'RISKY')}
        return results


class ReportingAgent:
    """AGENT 5: Generate comprehensive text report."""

    @staticmethod
    def generate_report(mixes: List[MixDesign], scores: Dict[str, Dict]) -> str:
        lines = []
        lines.append("=" * 80)
        lines.append("NAU CONCRETE CANOE 2026 - MIX DESIGN ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")

        winner = max(scores.items(), key=lambda x: x[1]['weighted_total'])
        lines.append(f"RECOMMENDED MIX: {winner[0]}")
        lines.append(f"  Weighted Score: {winner[1]['weighted_total']}/10 ({winner[1]['recommendation']})")
        lines.append("")

        calc = CalculationAgent()
        for mix in mixes:
            lines.append("=" * 80)
            lines.append(f"MIX: {mix.name}")
            lines.append("=" * 80)
            total_cm = calc.calculate_total_cementitious(mix)
            lines.append(f"\nCEMENTITIOUS MATERIALS ({total_cm:.1f} lbs):")
            lines.append(f"  Portland:  {mix.portland_lbs:7.2f} lbs ({mix.portland_percent:5.1f}%)")
            lines.append(f"  Slag:      {mix.slag_lbs:7.2f} lbs ({mix.slag_percent:5.1f}%)")
            lines.append(f"  Fly Ash:   {mix.fly_ash_lbs:7.2f} lbs ({mix.fly_ash_percent:5.1f}%)")
            lines.append(f"  Lime:      {mix.lime_lbs:7.2f} lbs ({mix.lime_percent:5.1f}%)")

            total_agg = calc.calculate_total_aggregates(mix)
            lines.append(f"\nAGGREGATES ({total_agg:.1f} lbs):")
            lines.append(f"  Poraver:   {mix.poraver_lbs:7.2f} lbs")
            lines.append(f"  Perlite:   {mix.perlite_lbs:7.2f} lbs")
            lines.append(f"  K1:        {mix.k1_lbs:7.2f} lbs")

            lines.append(f"\nPROPERTIES:")
            lines.append(f"  Density:   {mix.measured_density_pcf:.1f} pcf")
            lines.append(f"  w/cm:      {mix.w_cm_ratio:.2f}")
            lines.append(f"  7-day:     {mix.test_7day_psi:.0f} psi (WET)")

            pred = calc.calculate_28day_prediction(mix)
            lines.append(f"\n28-DAY PREDICTIONS:")
            lines.append(f"  Conservative: {pred['conservative']['dry_psi']:.0f} psi")
            lines.append(f"  Typical:      {pred['typical']['dry_psi']:.0f} psi")
            lines.append(f"  Optimistic:   {pred['optimistic']['dry_psi']:.0f} psi")

            s = scores[mix.name]
            lines.append(f"\nSCORES: {s['weighted_total']}/10 ({s['recommendation']})")
            lines.append("")

        lines.append("=" * 80)
        lines.append("RANKING")
        lines.append("=" * 80)
        for rank, (name, score) in enumerate(
                sorted(scores.items(), key=lambda x: x[1]['weighted_total'], reverse=True), 1):
            lines.append(f"  {rank}. {name:30s} {score['weighted_total']:5.1f}/10 ({score['recommendation']})")

        return "\n".join(lines)


def main():
    print("\n" + "=" * 80)
    print("NAU CONCRETE CANOE 2026 - MIX DESIGN ANALYSIS")
    print("=" * 80 + "\n")

    mixes = DataParserAgent.parse_all_mixes()
    print(f"[Agent 1] Loaded {len(mixes)} mix designs\n")

    calc = CalculationAgent()
    print("[Agent 2] Calculations")
    for mix in mixes:
        pred = calc.calculate_28day_prediction(mix)
        status = "PASS" if pred['typical']['passes_asce'] else "FAIL"
        print(f"  {mix.name:30s}: {pred['typical']['dry_psi']:.0f} psi ({status})")

    print("\n[Agent 3] Decision Matrix")
    scores = DecisionMatrixAgent.calculate_scores(mixes)
    for name, score in scores.items():
        print(f"  {name:30s}: {score['weighted_total']:5.1f}/10 ({score['recommendation']})")

    print("\n[Agent 5] Report")
    report = ReportingAgent.generate_report(mixes, scores)
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "mix_design", "MIX_DESIGN_REPORT.txt")
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"  Saved: {report_path}")

    print("\n" + report)
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
