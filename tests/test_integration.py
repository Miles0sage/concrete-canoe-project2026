"""Integration tests: end-to-end analysis pipeline for all 3 designs."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from calculations.concrete_canoe_calculator import run_complete_analysis


# ASCE competition thresholds (from generate_3_best_designs.py)
MIN_FB_IN = 6.0
MIN_GM_IN = 6.0
MIN_SF = 2.0
CWP = 0.65  # realistic waterplane coefficient


class TestDesignA:
    """Design A: 192\" x 32\" x 17\", Optimal (Lightest)."""

    @pytest.fixture
    def results(self):
        # 871 lbs = old loaded weight (canoe+crew); pass crew_weight_lbs=0
        # to avoid double-counting since calculator now adds crew internally
        return run_complete_analysis(
            hull_length_in=192, hull_beam_in=32, hull_depth_in=17,
            hull_thickness_in=0.5, concrete_weight_lbs=871,
            flexural_strength_psi=1500, waterplane_form_factor=CWP,
            crew_weight_lbs=0,
        )

    def test_returns_dict(self, results):
        assert isinstance(results, dict)
        assert "freeboard" in results
        assert "stability" in results
        assert "structural" in results

    def test_freeboard_passes(self, results):
        assert results["freeboard"]["freeboard_in"] >= MIN_FB_IN

    def test_gm_passes(self, results):
        assert results["stability"]["gm_in"] >= MIN_GM_IN

    def test_sf_passes(self, results):
        assert results["structural"]["safety_factor"] >= MIN_SF

    def test_overall_pass(self, results):
        fb = results["freeboard"]["freeboard_in"] >= MIN_FB_IN
        gm = results["stability"]["gm_in"] >= MIN_GM_IN
        sf = results["structural"]["safety_factor"] >= MIN_SF
        assert fb and gm and sf


class TestDesignB:
    """Design B: 196\" x 34\" x 18\", Conservative."""

    @pytest.fixture
    def results(self):
        return run_complete_analysis(
            hull_length_in=196, hull_beam_in=34, hull_depth_in=18,
            hull_thickness_in=0.5, concrete_weight_lbs=885,
            flexural_strength_psi=1500, waterplane_form_factor=CWP,
            crew_weight_lbs=0,
        )

    def test_freeboard_passes(self, results):
        assert results["freeboard"]["freeboard_in"] >= MIN_FB_IN

    def test_gm_passes(self, results):
        assert results["stability"]["gm_in"] >= MIN_GM_IN

    def test_sf_passes(self, results):
        assert results["structural"]["safety_factor"] >= MIN_SF


class TestDesignC:
    """Design C: 216\" x 36\" x 18\", Traditional."""

    @pytest.fixture
    def results(self):
        return run_complete_analysis(
            hull_length_in=216, hull_beam_in=36, hull_depth_in=18,
            hull_thickness_in=0.5, concrete_weight_lbs=911,
            flexural_strength_psi=1500, waterplane_form_factor=CWP,
            crew_weight_lbs=0,
        )

    def test_freeboard_passes(self, results):
        assert results["freeboard"]["freeboard_in"] >= MIN_FB_IN

    def test_gm_passes(self, results):
        assert results["stability"]["gm_in"] >= MIN_GM_IN

    def test_sf_passes(self, results):
        assert results["structural"]["safety_factor"] >= MIN_SF


class TestPipelineConsistency:
    """Cross-design consistency checks."""

    def _run(self, L, B, D, wt):
        return run_complete_analysis(
            hull_length_in=L, hull_beam_in=B, hull_depth_in=D,
            hull_thickness_in=0.5, concrete_weight_lbs=wt,
            flexural_strength_psi=1500, waterplane_form_factor=CWP,
            crew_weight_lbs=0,
        )

    def test_heavier_means_less_freeboard(self):
        r_light = self._run(192, 32, 17, 500)
        r_heavy = self._run(192, 32, 17, 1000)
        assert r_light["freeboard"]["freeboard_in"] > r_heavy["freeboard"]["freeboard_in"]

    def test_wider_means_more_stable(self):
        r_narrow = self._run(192, 28, 17, 871)
        r_wide = self._run(192, 36, 17, 871)
        assert r_wide["stability"]["gm_in"] > r_narrow["stability"]["gm_in"]

    def test_deeper_means_more_freeboard(self):
        r_shallow = self._run(192, 32, 14, 871)
        r_deep = self._run(192, 32, 20, 871)
        assert r_deep["freeboard"]["freeboard_in"] > r_shallow["freeboard"]["freeboard_in"]

    def test_all_three_designs_pass(self):
        designs = [
            (192, 32, 17, 871),
            (196, 34, 18, 885),
            (216, 36, 18, 911),
        ]
        for L, B, D, wt in designs:
            r = self._run(L, B, D, wt)
            fb = r["freeboard"]["freeboard_in"] >= MIN_FB_IN
            gm = r["stability"]["gm_in"] >= MIN_GM_IN
            sf = r["structural"]["safety_factor"] >= MIN_SF
            assert fb and gm and sf, f"Design {L}x{B}x{D} failed"
