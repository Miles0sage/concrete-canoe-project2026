"""Tests for HullGeometry class and dimensional conversions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from calculations.concrete_canoe_calculator import HullGeometry, INCHES_PER_FOOT


class TestHullGeometry:
    """Test HullGeometry dataclass properties."""

    def test_basic_creation(self):
        hull = HullGeometry(length_in=192, beam_in=32, depth_in=17, thickness_in=0.5)
        assert hull.length_in == 192
        assert hull.beam_in == 32
        assert hull.depth_in == 17
        assert hull.thickness_in == 0.5

    def test_ft_conversions(self):
        hull = HullGeometry(length_in=192, beam_in=36, depth_in=18, thickness_in=0.5)
        assert hull.length_ft == pytest.approx(16.0)
        assert hull.beam_ft == pytest.approx(3.0)
        assert hull.depth_ft == pytest.approx(1.5)
        assert hull.thickness_ft == pytest.approx(0.5 / 12)

    def test_zero_dimensions(self):
        hull = HullGeometry(length_in=0, beam_in=0, depth_in=0, thickness_in=0)
        assert hull.length_ft == 0.0
        assert hull.beam_ft == 0.0
        assert hull.depth_ft == 0.0
        assert hull.thickness_ft == 0.0

    def test_design_a_dimensions(self):
        hull = HullGeometry(length_in=192, beam_in=32, depth_in=17, thickness_in=0.5)
        assert hull.length_ft == pytest.approx(16.0)
        assert hull.beam_ft == pytest.approx(32 / 12, rel=1e-6)

    def test_design_b_dimensions(self):
        hull = HullGeometry(length_in=196, beam_in=34, depth_in=18, thickness_in=0.5)
        assert hull.length_ft == pytest.approx(196 / 12, rel=1e-6)

    def test_design_c_dimensions(self):
        hull = HullGeometry(length_in=216, beam_in=36, depth_in=18, thickness_in=0.5)
        assert hull.length_ft == pytest.approx(18.0)
        assert hull.beam_ft == pytest.approx(3.0)

    def test_dimensional_consistency(self):
        hull = HullGeometry(length_in=180, beam_in=30, depth_in=15, thickness_in=0.75)
        assert hull.length_in == hull.length_ft * INCHES_PER_FOOT
        assert hull.beam_in == hull.beam_ft * INCHES_PER_FOOT
        assert hull.depth_in == hull.depth_ft * INCHES_PER_FOOT
        assert hull.thickness_in == hull.thickness_ft * INCHES_PER_FOOT
