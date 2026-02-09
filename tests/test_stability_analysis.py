"""Tests for stability calculations: metacentric height GM."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from calculations.concrete_canoe_calculator import metacentric_height_approx


class TestMetacentricHeight:
    def test_basic_gm_positive(self):
        """A wide, shallow-draft hull should have positive GM."""
        gm = metacentric_height_approx(
            beam_ft=3.0, draft_ft=0.5, depth_ft=1.5, cog_height_approx_ft=0.6
        )
        assert gm > 0

    def test_zero_draft(self):
        gm = metacentric_height_approx(
            beam_ft=3.0, draft_ft=0, depth_ft=1.5, cog_height_approx_ft=0.6
        )
        assert gm == 0.0

    def test_wider_beam_more_stable(self):
        """Wider beam should give higher GM (more stable)."""
        gm_narrow = metacentric_height_approx(
            beam_ft=2.0, draft_ft=0.5, depth_ft=1.5, cog_height_approx_ft=0.6
        )
        gm_wide = metacentric_height_approx(
            beam_ft=3.0, draft_ft=0.5, depth_ft=1.5, cog_height_approx_ft=0.6
        )
        assert gm_wide > gm_narrow

    def test_higher_cog_less_stable(self):
        """Higher center of gravity should reduce GM."""
        gm_low = metacentric_height_approx(
            beam_ft=3.0, draft_ft=0.5, depth_ft=1.5, cog_height_approx_ft=0.4
        )
        gm_high = metacentric_height_approx(
            beam_ft=3.0, draft_ft=0.5, depth_ft=1.5, cog_height_approx_ft=0.8
        )
        assert gm_low > gm_high

    def test_design_a_gm_passes(self):
        """Design A loaded should have GM > 6 inches."""
        draft_ft = 0.5  # approximate
        gm = metacentric_height_approx(
            beam_ft=32/12, draft_ft=draft_ft, depth_ft=17/12,
            cog_height_approx_ft=(17/12)*0.45
        )
        gm_in = gm * 12
        assert gm_in > 6.0

    def test_gm_components(self):
        """Verify GM = KB + BM - KG formula."""
        beam, draft, depth, cog = 3.0, 0.5, 1.5, 0.6
        kb = draft / 2
        bm = beam**2 / (12 * draft)
        kg = cog
        expected = kb + bm - kg
        actual = metacentric_height_approx(beam, draft, depth, cog)
        assert actual == pytest.approx(expected, rel=1e-6)

    def test_capsize_scenario(self):
        """Very narrow hull with high CG should have negative GM."""
        gm = metacentric_height_approx(
            beam_ft=0.5, draft_ft=1.0, depth_ft=2.0,
            cog_height_approx_ft=1.5
        )
        assert gm < 0  # unstable
