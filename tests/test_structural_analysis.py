"""Tests for structural calculations: bending, section modulus, safety factor."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from calculations.concrete_canoe_calculator import (
    bending_moment_uniform_load,
    section_modulus_rectangular,
    bending_stress_psi,
    safety_factor,
)


class TestBendingMoment:
    def test_basic_moment(self):
        """wL²/8 for uniform load on simply supported beam."""
        M = bending_moment_uniform_load(w_lbs_per_ft=100, length_ft=10)
        assert M == pytest.approx(100 * 100 / 8, rel=1e-6)

    def test_zero_load(self):
        assert bending_moment_uniform_load(0, 10) == 0.0

    def test_zero_length(self):
        assert bending_moment_uniform_load(100, 0) == 0.0

    def test_moment_scales_quadratically(self):
        M1 = bending_moment_uniform_load(10, 10)
        M2 = bending_moment_uniform_load(10, 20)
        assert M2 == pytest.approx(M1 * 4, rel=1e-6)


class TestSectionModulus:
    def test_basic_section_modulus(self):
        S = section_modulus_rectangular(b_in=10, h_in=6)
        assert S == pytest.approx(10 * 36 / 6, rel=1e-6)

    def test_zero_dimension(self):
        assert section_modulus_rectangular(0, 6) == 0.0
        assert section_modulus_rectangular(10, 0) == 0.0

    def test_design_a_section(self):
        S = section_modulus_rectangular(32, 16.5)  # beam × (depth - thickness)
        assert S > 0
        assert S == pytest.approx(32 * 16.5**2 / 6, rel=1e-6)


class TestBendingStress:
    def test_basic_stress(self):
        sigma = bending_stress_psi(100, 10)  # 100 lb-ft, 10 in³
        assert sigma == pytest.approx(100 * 12 / 10, rel=1e-6)

    def test_zero_section_modulus(self):
        assert bending_stress_psi(100, 0) == 0.0

    def test_zero_moment(self):
        assert bending_stress_psi(0, 10) == 0.0


class TestSafetyFactor:
    def test_basic_sf(self):
        sf = safety_factor(1500, 15)
        assert sf == pytest.approx(100, rel=1e-6)

    def test_exactly_two(self):
        sf = safety_factor(100, 50)
        assert sf == pytest.approx(2.0, rel=1e-6)

    def test_zero_stress(self):
        assert safety_factor(1500, 0) == 0.0

    def test_design_a_sf_above_minimum(self):
        """Design A should have SF >> 2.0."""
        M = bending_moment_uniform_load(871 / 16, 16)
        S = section_modulus_rectangular(32, 16.5)
        sigma = bending_stress_psi(M, S)
        sf = safety_factor(1500, sigma)
        assert sf > 2.0

    def test_sf_increases_with_strength(self):
        sf1 = safety_factor(1000, 50)
        sf2 = safety_factor(2000, 50)
        assert sf2 > sf1
