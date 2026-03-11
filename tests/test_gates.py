# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for gate matrix correctness and properties."""

import math

import numpy as np
import pytest

from quantsdk.gates import (
    CXGate,
    CZGate,
    HGate,
    IGate,
    RXGate,
    RYGate,
    RZGate,
    SGate,
    SwapGate,
    TGate,
    ToffoliGate,
    U3Gate,
    XGate,
    YGate,
    ZGate,
)


def is_unitary(matrix: np.ndarray, tol: float = 1e-10) -> bool:
    """Check if a matrix is unitary: U† U = I."""
    n = matrix.shape[0]
    product = matrix.conj().T @ matrix
    return np.allclose(product, np.eye(n), atol=tol)


class TestSingleQubitGateMatrices:
    """Verify that single-qubit gate matrices are correct and unitary."""

    def test_h_gate_unitary(self):
        assert is_unitary(HGate(0).matrix())

    def test_h_gate_values(self):
        m = HGate(0).matrix()
        expected = np.array([[1, 1], [1, -1]]) / math.sqrt(2)
        np.testing.assert_allclose(m, expected)

    def test_h_squared_is_identity(self):
        """H² = I"""
        h = HGate(0).matrix()
        np.testing.assert_allclose(h @ h, np.eye(2), atol=1e-10)

    def test_x_gate(self):
        m = XGate(0).matrix()
        np.testing.assert_allclose(m, np.array([[0, 1], [1, 0]]))
        assert is_unitary(m)

    def test_x_squared_is_identity(self):
        """X² = I"""
        x = XGate(0).matrix()
        np.testing.assert_allclose(x @ x, np.eye(2), atol=1e-10)

    def test_y_gate(self):
        m = YGate(0).matrix()
        np.testing.assert_allclose(m, np.array([[0, -1j], [1j, 0]]))
        assert is_unitary(m)

    def test_z_gate(self):
        m = ZGate(0).matrix()
        np.testing.assert_allclose(m, np.array([[1, 0], [0, -1]]))
        assert is_unitary(m)

    def test_s_gate(self):
        m = SGate(0).matrix()
        expected = np.array([[1, 0], [0, 1j]])
        np.testing.assert_allclose(m, expected)
        assert is_unitary(m)

    def test_s_squared_is_z(self):
        """S² = Z"""
        s = SGate(0).matrix()
        z = ZGate(0).matrix()
        np.testing.assert_allclose(s @ s, z, atol=1e-10)

    def test_t_gate(self):
        m = TGate(0).matrix()
        assert is_unitary(m)

    def test_t_squared_is_s(self):
        """T² = S"""
        t = TGate(0).matrix()
        s = SGate(0).matrix()
        np.testing.assert_allclose(t @ t, s, atol=1e-10)

    def test_identity_gate(self):
        m = IGate(0).matrix()
        np.testing.assert_allclose(m, np.eye(2))


class TestParametricGateMatrices:
    """Verify parametric gate matrices."""

    def test_rx_unitary(self):
        for theta in [0, math.pi / 4, math.pi / 2, math.pi, 2 * math.pi]:
            assert is_unitary(RXGate(0, theta).matrix())

    def test_rx_zero_is_identity(self):
        """RX(0) = I"""
        np.testing.assert_allclose(RXGate(0, 0).matrix(), np.eye(2), atol=1e-10)

    def test_rx_pi_is_minus_i_x(self):
        """RX(π) = -iX"""
        rx = RXGate(0, math.pi).matrix()
        x = XGate(0).matrix()
        np.testing.assert_allclose(rx, -1j * x, atol=1e-10)

    def test_ry_unitary(self):
        for theta in [0, math.pi / 4, math.pi / 2, math.pi]:
            assert is_unitary(RYGate(0, theta).matrix())

    def test_rz_unitary(self):
        for theta in [0, math.pi / 4, math.pi / 2, math.pi]:
            assert is_unitary(RZGate(0, theta).matrix())

    def test_u3_unitary(self):
        for theta, phi, lam in [(0, 0, 0), (math.pi, 0, math.pi), (math.pi / 2, 0, 0)]:
            assert is_unitary(U3Gate(0, theta, phi, lam).matrix())

    def test_u3_zero_is_identity(self):
        """U3(0, 0, 0) = I"""
        np.testing.assert_allclose(U3Gate(0, 0, 0, 0).matrix(), np.eye(2), atol=1e-10)


class TestTwoQubitGateMatrices:
    """Verify two-qubit gate matrices."""

    def test_cx_unitary(self):
        assert is_unitary(CXGate(0, 1).matrix())

    def test_cx_matrix(self):
        expected = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex
        )
        np.testing.assert_allclose(CXGate(0, 1).matrix(), expected)

    def test_cz_unitary(self):
        assert is_unitary(CZGate(0, 1).matrix())

    def test_swap_unitary(self):
        assert is_unitary(SwapGate(0, 1).matrix())

    def test_swap_squared_is_identity(self):
        """SWAP² = I"""
        s = SwapGate(0, 1).matrix()
        np.testing.assert_allclose(s @ s, np.eye(4), atol=1e-10)


class TestThreeQubitGateMatrices:
    """Verify three-qubit gate matrices."""

    def test_toffoli_unitary(self):
        assert is_unitary(ToffoliGate(0, 1, 2).matrix())

    def test_toffoli_matrix_size(self):
        m = ToffoliGate(0, 1, 2).matrix()
        assert m.shape == (8, 8)


class TestGateProperties:
    """Test general gate properties."""

    def test_gate_is_frozen(self):
        """Gates should be immutable (frozen dataclass)."""
        g = HGate(0)
        with pytest.raises(AttributeError):
            g.name = "X"  # type: ignore

    def test_gate_repr(self):
        g = RXGate(0, math.pi)
        r = repr(g)
        assert "RX" in r
        assert "qubits=(0,)" in r
