"""Tests for hydrostatic calculations: displacement, draft, freeboard."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from calculations.concrete_canoe_calculator import (
    displacement_volume,
    waterplane_approximation,
    draft_from_displacement,
    freeboard,
    WATER_DENSITY_LB_PER_FT3,
)


class TestDisplacement:
    def test_archimedes_basic(self):
        vol = displacement_volume(62.4)
        assert vol == pytest.approx(1.0, rel=1e-6)

    def test_zero_weight(self):
        assert displacement_volume(0) == 0.0

    def test_heavy_load(self):
        vol = displacement_volume(624)
        assert vol == pytest.approx(10.0, rel=1e-6)

    def test_canoe_weight_276(self):
        vol = displacement_volume(276)
        assert vol == pytest.approx(276 / 62.4, rel=1e-6)


class TestWaterplane:
    def test_basic_area(self):
        area = waterplane_approximation(16, 2.5, 0.10)
        assert area == pytest.approx(4.0, rel=1e-6)

    def test_zero_dimensions(self):
        assert waterplane_approximation(0, 2.5, 0.10) == 0.0
        assert waterplane_approximation(16, 0, 0.10) == 0.0

    def test_realistic_cwp(self):
        area = waterplane_approximation(16, 2.667, 0.65)
        assert area == pytest.approx(16 * 2.667 * 0.65, rel=1e-4)


class TestDraft:
    def test_basic_draft(self):
        draft = draft_from_displacement(1.0, 10.0)
        assert draft == pytest.approx(0.1, rel=1e-6)

    def test_zero_waterplane(self):
        assert draft_from_displacement(1.0, 0) == 0.0

    def test_zero_displacement(self):
        assert draft_from_displacement(0, 10.0) == 0.0

    def test_realistic_scenario(self):
        """Design A loaded: ~871 lbs, Cwp=0.65"""
        disp = 871 / 62.4
        wp = 16 * (32/12) * 0.65
        draft = draft_from_displacement(disp, wp)
        draft_in = draft * 12
        assert 4 < draft_in < 10


class TestFreeboard:
    def test_positive_freeboard(self):
        fb = freeboard(1.5, 0.5)
        assert fb == pytest.approx(1.0, rel=1e-6)

    def test_zero_freeboard(self):
        fb = freeboard(1.0, 1.0)
        assert fb == 0.0

    def test_negative_clamped(self):
        fb = freeboard(1.0, 2.0)
        assert fb == 0.0

    def test_design_a_freeboard(self):
        """Design A should have freeboard > 6 inches."""
        disp = 871 / 62.4
        wp = 16 * (32/12) * 0.65
        draft = draft_from_displacement(disp, wp)
        fb = freeboard(17/12, draft)
        fb_in = fb * 12
        assert fb_in > 6.0

    def test_extreme_loading(self):
        """Extreme load (2000 lbs) should reduce freeboard significantly."""
        disp = 2000 / 62.4
        wp = 16 * (32/12) * 0.65
        draft = draft_from_displacement(disp, wp)
        fb = freeboard(17/12, draft)
        assert fb < 17/12  # less than full depth
