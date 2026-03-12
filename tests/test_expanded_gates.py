# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for expanded gate library (27 new gates, 50+ total)."""

import math

import numpy as np
import pytest

from quantsdk.circuit import Circuit
from quantsdk.gates import (
    GATE_MAP,
    CCZGate,
    CHGate,
    CPhaseGate,
    CRXGate,
    CRYGate,
    CRZGate,
    CSdgGate,
    CSGate,
    CSXGate,
    CU1Gate,
    CU3Gate,
    CYGate,
    DCXGate,
    ECRGate,
    PhaseGate,
    Reset,
    RGate,
    RXXGate,
    RYYGate,
    RZXGate,
    RZZGate,
    SdgGate,
    SGate,
    SXdgGate,
    SXGate,
    TdgGate,
    TGate,
    U1Gate,
    U2Gate,
    U3Gate,
    XGate,
    ZGate,
    iSwapGate,
)


def is_unitary(matrix: np.ndarray, tol: float = 1e-10) -> bool:
    """Check if a matrix is unitary: U dagger U = I."""
    n = matrix.shape[0]
    product = matrix.conj().T @ matrix
    return np.allclose(product, np.eye(n), atol=tol)


# ─── Test Gate Count ───


class TestGateCount:
    """Verify we have 50+ gates in GATE_MAP."""

    def test_gate_map_has_50_plus_entries(self):
        assert len(GATE_MAP) >= 50, f"GATE_MAP has {len(GATE_MAP)} entries, need 50+"

    def test_gate_map_unique_classes(self):
        unique_classes = set(GATE_MAP.values())
        assert len(unique_classes) >= 30, f"Only {len(unique_classes)} unique gate classes"


# ─── Test New Single-Qubit Gate Matrices ───


class TestNewSingleQubitGates:
    """Test Sdg, Tdg, SX, SXdg gate matrices."""

    def test_sdg_unitary(self):
        assert is_unitary(SdgGate(0).matrix())

    def test_sdg_is_adjoint_of_s(self):
        """Sdg = S dagger"""
        s = SGate(0).matrix()
        sdg = SdgGate(0).matrix()
        np.testing.assert_allclose(sdg, s.conj().T, atol=1e-10)

    def test_s_sdg_is_identity(self):
        """S * Sdg = I"""
        product = SGate(0).matrix() @ SdgGate(0).matrix()
        np.testing.assert_allclose(product, np.eye(2), atol=1e-10)

    def test_tdg_unitary(self):
        assert is_unitary(TdgGate(0).matrix())

    def test_tdg_is_adjoint_of_t(self):
        """Tdg = T dagger"""
        t = TGate(0).matrix()
        tdg = TdgGate(0).matrix()
        np.testing.assert_allclose(tdg, t.conj().T, atol=1e-10)

    def test_t_tdg_is_identity(self):
        """T * Tdg = I"""
        product = TGate(0).matrix() @ TdgGate(0).matrix()
        np.testing.assert_allclose(product, np.eye(2), atol=1e-10)

    def test_sx_unitary(self):
        assert is_unitary(SXGate(0).matrix())

    def test_sx_squared_is_x(self):
        """SX * SX = X"""
        sx = SXGate(0).matrix()
        x = XGate(0).matrix()
        np.testing.assert_allclose(sx @ sx, x, atol=1e-10)

    def test_sxdg_unitary(self):
        assert is_unitary(SXdgGate(0).matrix())

    def test_sxdg_is_adjoint_of_sx(self):
        """SXdg = SX dagger"""
        sx = SXGate(0).matrix()
        sxdg = SXdgGate(0).matrix()
        np.testing.assert_allclose(sxdg, sx.conj().T, atol=1e-10)

    def test_sx_sxdg_is_identity(self):
        """SX * SXdg = I"""
        product = SXGate(0).matrix() @ SXdgGate(0).matrix()
        np.testing.assert_allclose(product, np.eye(2), atol=1e-10)


# ─── Test New Parametric Single-Qubit Gates ───


class TestNewParametricGates:
    """Test Phase, U1, U2, R gate matrices."""

    def test_phase_unitary(self):
        for lam in [0, math.pi / 4, math.pi / 2, math.pi]:
            assert is_unitary(PhaseGate(0, lam).matrix())

    def test_phase_zero_is_identity(self):
        np.testing.assert_allclose(PhaseGate(0, 0).matrix(), np.eye(2), atol=1e-10)

    def test_phase_pi_is_z(self):
        """P(pi) = Z"""
        p = PhaseGate(0, math.pi).matrix()
        z = ZGate(0).matrix()
        np.testing.assert_allclose(p, z, atol=1e-10)

    def test_phase_pi2_is_s(self):
        """P(pi/2) = S"""
        p = PhaseGate(0, math.pi / 2).matrix()
        s = SGate(0).matrix()
        np.testing.assert_allclose(p, s, atol=1e-10)

    def test_u1_equals_phase(self):
        """U1 and Phase produce the same matrix."""
        for lam in [0, math.pi / 4, math.pi]:
            np.testing.assert_allclose(
                U1Gate(0, lam).matrix(), PhaseGate(0, lam).matrix(), atol=1e-10
            )

    def test_u2_unitary(self):
        for phi, lam in [(0, 0), (math.pi / 2, math.pi), (0, math.pi)]:
            assert is_unitary(U2Gate(0, phi, lam).matrix())

    def test_u2_matches_u3_pi2(self):
        """U2(phi, lam) = U3(pi/2, phi, lam)"""
        for phi, lam in [(0, math.pi), (math.pi / 2, 0)]:
            u2 = U2Gate(0, phi, lam).matrix()
            u3 = U3Gate(0, math.pi / 2, phi, lam).matrix()
            np.testing.assert_allclose(u2, u3, atol=1e-10)

    def test_r_unitary(self):
        for theta, phi in [(0, 0), (math.pi, 0), (math.pi / 2, math.pi / 4)]:
            assert is_unitary(RGate(0, theta, phi).matrix())

    def test_r_zero_is_identity(self):
        np.testing.assert_allclose(RGate(0, 0, 0).matrix(), np.eye(2), atol=1e-10)


# ─── Test Controlled Gates ───


class TestControlledGates:
    """Test CY, CH, CS, CSdg, CRX, CRY, CRZ, CPhase, CU1, CU3, CSX."""

    def test_cy_unitary(self):
        assert is_unitary(CYGate(0, 1).matrix())

    def test_ch_unitary(self):
        assert is_unitary(CHGate(0, 1).matrix())

    def test_cs_unitary(self):
        assert is_unitary(CSGate(0, 1).matrix())

    def test_csdg_unitary(self):
        assert is_unitary(CSdgGate(0, 1).matrix())

    def test_cs_csdg_product(self):
        """CS * CSdg = I (for the lower-right block)"""
        cs = CSGate(0, 1).matrix()
        csdg = CSdgGate(0, 1).matrix()
        np.testing.assert_allclose(cs @ csdg, np.eye(4), atol=1e-10)

    def test_crx_unitary(self):
        for theta in [0, math.pi / 4, math.pi, 2 * math.pi]:
            assert is_unitary(CRXGate(0, 1, theta).matrix())

    def test_crx_zero_is_identity(self):
        np.testing.assert_allclose(CRXGate(0, 1, 0).matrix(), np.eye(4), atol=1e-10)

    def test_cry_unitary(self):
        for theta in [0, math.pi / 4, math.pi]:
            assert is_unitary(CRYGate(0, 1, theta).matrix())

    def test_crz_unitary(self):
        for theta in [0, math.pi / 4, math.pi]:
            assert is_unitary(CRZGate(0, 1, theta).matrix())

    def test_cphase_unitary(self):
        for lam in [0, math.pi / 4, math.pi]:
            assert is_unitary(CPhaseGate(0, 1, lam).matrix())

    def test_cphase_pi_is_cz(self):
        """CP(pi) = CZ"""
        from quantsdk.gates import CZGate

        cp = CPhaseGate(0, 1, math.pi).matrix()
        cz = CZGate(0, 1).matrix()
        np.testing.assert_allclose(cp, cz, atol=1e-10)

    def test_cu1_equals_cphase(self):
        """CU1 and CPhase produce the same matrix."""
        for lam in [0, math.pi / 4, math.pi]:
            np.testing.assert_allclose(
                CU1Gate(0, 1, lam).matrix(), CPhaseGate(0, 1, lam).matrix(), atol=1e-10
            )

    def test_cu3_unitary(self):
        for theta, phi, lam in [(0, 0, 0), (math.pi, 0, math.pi)]:
            assert is_unitary(CU3Gate(0, 1, theta, phi, lam).matrix())

    def test_cu3_zero_is_identity(self):
        np.testing.assert_allclose(CU3Gate(0, 1, 0, 0, 0).matrix(), np.eye(4), atol=1e-10)

    def test_csx_unitary(self):
        assert is_unitary(CSXGate(0, 1).matrix())


# ─── Test Two-Qubit Rotation Gates ───


class TestTwoQubitRotations:
    """Test RXX, RYY, RZX gates."""

    def test_rxx_unitary(self):
        for theta in [0, math.pi / 4, math.pi]:
            assert is_unitary(RXXGate(0, 1, theta).matrix())

    def test_rxx_zero_is_identity(self):
        np.testing.assert_allclose(RXXGate(0, 1, 0).matrix(), np.eye(4), atol=1e-10)

    def test_ryy_unitary(self):
        for theta in [0, math.pi / 4, math.pi]:
            assert is_unitary(RYYGate(0, 1, theta).matrix())

    def test_ryy_zero_is_identity(self):
        np.testing.assert_allclose(RYYGate(0, 1, 0).matrix(), np.eye(4), atol=1e-10)

    def test_rzx_unitary(self):
        for theta in [0, math.pi / 4, math.pi]:
            assert is_unitary(RZXGate(0, 1, theta).matrix())

    def test_rzx_zero_is_identity(self):
        np.testing.assert_allclose(RZXGate(0, 1, 0).matrix(), np.eye(4), atol=1e-10)

    def test_rzz_still_works(self):
        """Existing RZZ gate still works correctly."""
        assert is_unitary(RZZGate(0, 1, math.pi / 4).matrix())


# ─── Test Two-Qubit Special Gates ───


class TestTwoQubitSpecialGates:
    """Test iSWAP, DCX, ECR."""

    def test_iswap_unitary(self):
        assert is_unitary(iSwapGate(0, 1).matrix())

    def test_iswap_squared(self):
        """iSWAP^2 = diag(1, -1, -1, 1)."""
        m = iSwapGate(0, 1).matrix()
        m2 = m @ m
        expected = np.diag([1, -1, -1, 1]).astype(complex)
        np.testing.assert_allclose(m2, expected, atol=1e-10)

    def test_dcx_unitary(self):
        assert is_unitary(DCXGate(0, 1).matrix())

    def test_ecr_unitary(self):
        assert is_unitary(ECRGate(0, 1).matrix())


# ─── Test Three-Qubit Gates ───


class TestCCZGate:
    """Test CCZ gate."""

    def test_ccz_unitary(self):
        assert is_unitary(CCZGate(0, 1, 2).matrix())

    def test_ccz_matrix_size(self):
        m = CCZGate(0, 1, 2).matrix()
        assert m.shape == (8, 8)

    def test_ccz_only_flips_111(self):
        """CCZ applies -1 phase only to |111>."""
        m = CCZGate(0, 1, 2).matrix()
        # Diagonal gate: all diagonal elements are 1 except last
        assert m[7, 7] == -1
        for i in range(7):
            assert m[i, i] == 1


# ─── Test Reset ───


class TestResetGate:
    """Test Reset gate."""

    def test_reset_is_not_unitary(self):
        with pytest.raises(NotImplementedError):
            Reset(0).matrix()

    def test_reset_name(self):
        assert Reset(0).name == "RESET"


# ─── Test Circuit Fluent API for New Gates ───


class TestCircuitFluentAPI:
    """Test that Circuit has fluent methods for all new gates."""

    def test_sdg_method(self):
        c = Circuit(1).sdg(0)
        assert c.gates[0].name == "Sdg"

    def test_tdg_method(self):
        c = Circuit(1).tdg(0)
        assert c.gates[0].name == "Tdg"

    def test_sx_method(self):
        c = Circuit(1).sx(0)
        assert c.gates[0].name == "SX"

    def test_sxdg_method(self):
        c = Circuit(1).sxdg(0)
        assert c.gates[0].name == "SXdg"

    def test_p_method(self):
        c = Circuit(1).p(0, math.pi)
        assert c.gates[0].name == "P"

    def test_u1_method(self):
        c = Circuit(1).u1(0, math.pi)
        assert c.gates[0].name == "U1"

    def test_u2_method(self):
        c = Circuit(1).u2(0, 0, math.pi)
        assert c.gates[0].name == "U2"

    def test_r_method(self):
        c = Circuit(1).r(0, math.pi, 0)
        assert c.gates[0].name == "R"

    def test_cy_method(self):
        c = Circuit(2).cy(0, 1)
        assert c.gates[0].name == "CY"

    def test_ch_method(self):
        c = Circuit(2).ch(0, 1)
        assert c.gates[0].name == "CH"

    def test_cs_method(self):
        c = Circuit(2).cs(0, 1)
        assert c.gates[0].name == "CS"

    def test_csdg_method(self):
        c = Circuit(2).csdg(0, 1)
        assert c.gates[0].name == "CSdg"

    def test_crx_method(self):
        c = Circuit(2).crx(0, 1, math.pi)
        assert c.gates[0].name == "CRX"

    def test_cry_method(self):
        c = Circuit(2).cry(0, 1, math.pi)
        assert c.gates[0].name == "CRY"

    def test_crz_method(self):
        c = Circuit(2).crz(0, 1, math.pi)
        assert c.gates[0].name == "CRZ"

    def test_cp_method(self):
        c = Circuit(2).cp(0, 1, math.pi)
        assert c.gates[0].name == "CP"

    def test_cu1_method(self):
        c = Circuit(2).cu1(0, 1, math.pi)
        assert c.gates[0].name == "CU1"

    def test_cu3_method(self):
        c = Circuit(2).cu3(0, 1, math.pi, 0, math.pi)
        assert c.gates[0].name == "CU3"

    def test_csx_method(self):
        c = Circuit(2).csx(0, 1)
        assert c.gates[0].name == "CSX"

    def test_rxx_method(self):
        c = Circuit(2).rxx(0, 1, math.pi)
        assert c.gates[0].name == "RXX"

    def test_ryy_method(self):
        c = Circuit(2).ryy(0, 1, math.pi)
        assert c.gates[0].name == "RYY"

    def test_rzx_method(self):
        c = Circuit(2).rzx(0, 1, math.pi)
        assert c.gates[0].name == "RZX"

    def test_iswap_method(self):
        c = Circuit(2).iswap(0, 1)
        assert c.gates[0].name == "iSWAP"

    def test_dcx_method(self):
        c = Circuit(2).dcx(0, 1)
        assert c.gates[0].name == "DCX"

    def test_ecr_method(self):
        c = Circuit(2).ecr(0, 1)
        assert c.gates[0].name == "ECR"

    def test_ccz_method(self):
        c = Circuit(3).ccz(0, 1, 2)
        assert c.gates[0].name == "CCZ"

    def test_reset_method(self):
        c = Circuit(1).reset(0)
        assert c.gates[0].name == "RESET"

    def test_fluent_chaining(self):
        """All new methods support fluent chaining."""
        c = (
            Circuit(3)
            .sdg(0)
            .tdg(0)
            .sx(0)
            .sxdg(0)
            .p(0, 0.5)
            .u1(0, 0.5)
            .u2(0, 0, 0.5)
            .r(0, 0.5, 0)
            .cy(0, 1)
            .ch(0, 1)
            .cs(0, 1)
            .csdg(0, 1)
            .crx(0, 1, 0.5)
            .cry(0, 1, 0.5)
            .crz(0, 1, 0.5)
            .cp(0, 1, 0.5)
            .cu1(0, 1, 0.5)
            .cu3(0, 1, 0.5, 0, 0)
            .csx(0, 1)
            .rxx(0, 1, 0.5)
            .ryy(0, 1, 0.5)
            .rzx(0, 1, 0.5)
            .iswap(0, 1)
            .dcx(0, 1)
            .ecr(0, 1)
            .ccz(0, 1, 2)
            .reset(0)
        )
        assert len(c) == 27


# ─── Test Simulation with New Gates ───


class TestSimulationWithNewGates:
    """Test that new gates work correctly in the simulator."""

    def test_sdg_simulation(self):
        """S followed by Sdg should give back |0>."""
        import quantsdk as qs

        c = qs.Circuit(1).s(0).sdg(0).measure_all()
        result = qs.run(c, shots=100, seed=42)
        assert result.counts.get("0", 0) == 100

    def test_sx_simulation(self):
        """SX twice should be X (flip |0> to |1>)."""
        import quantsdk as qs

        c = qs.Circuit(1).sx(0).sx(0).measure_all()
        result = qs.run(c, shots=100, seed=42)
        assert result.counts.get("1", 0) == 100

    def test_phase_gate_simulation(self):
        """P(pi) on |+> should give |->  (measure ~50/50 still)."""
        import quantsdk as qs

        c = qs.Circuit(1).h(0).p(0, math.pi).h(0).measure_all()
        result = qs.run(c, shots=100, seed=42)
        # H P(pi) H = X, so should measure |1>
        assert result.counts.get("1", 0) == 100

    def test_cy_simulation(self):
        """CY with control=|1> should flip target."""
        import quantsdk as qs

        c = qs.Circuit(2).x(0).cy(0, 1).measure_all()
        result = qs.run(c, shots=100, seed=42)
        # After X|0> -> |1>, CY flips target: result should be |1,1> = "11"
        # But CY applies Y, which gives i|1> phase, measurement is still |11>
        assert "11" in result.counts

    def test_iswap_simulation(self):
        """iSWAP on |10> should give i|01>."""
        import quantsdk as qs

        c = qs.Circuit(2).x(0).iswap(0, 1).measure_all()
        result = qs.run(c, shots=100, seed=42)
        assert result.counts.get("01", 0) == 100

    def test_ccz_simulation(self):
        """CCZ on |111> should add -1 phase (measure still |111>)."""
        import quantsdk as qs

        c = qs.Circuit(3).x(0).x(1).x(2).ccz(0, 1, 2).measure_all()
        result = qs.run(c, shots=100, seed=42)
        assert result.counts.get("111", 0) == 100

    def test_reset_simulation(self):
        """Reset should bring qubit back to |0>."""
        import quantsdk as qs

        c = qs.Circuit(1).x(0).reset(0).measure_all()
        result = qs.run(c, shots=100, seed=42)
        assert result.counts.get("0", 0) == 100

    def test_reset_entangled(self):
        """Reset one qubit of an entangled pair."""
        import quantsdk as qs

        c = qs.Circuit(2).h(0).cx(0, 1).reset(0).measure_all()
        result = qs.run(c, shots=1000, seed=42)
        # After reset qubit 0, qubit 0 is |0>, qubit 1 is 50/50
        for bitstring in result.counts:
            assert bitstring[0] == "0"  # qubit 0 is always 0


# ─── Test OpenQASM Roundtrip for New Gates ───


class TestOpenQASMNewGates:
    """Test OpenQASM export/import for new gates."""

    def test_sdg_roundtrip(self):
        from quantsdk.interop.openqasm import from_openqasm, to_openqasm

        c = Circuit(1).sdg(0)
        qasm = to_openqasm(c)
        assert "sdg" in qasm
        c2 = from_openqasm(qasm)
        assert c2.gates[0].name == "Sdg"

    def test_phase_roundtrip(self):
        from quantsdk.interop.openqasm import from_openqasm, to_openqasm

        c = Circuit(1).p(0, math.pi / 4)
        qasm = to_openqasm(c)
        assert "p(" in qasm
        c2 = from_openqasm(qasm)
        assert c2.gates[0].name == "P"
        np.testing.assert_allclose(c2.gates[0].params[0], math.pi / 4, atol=1e-10)

    def test_crz_roundtrip(self):
        from quantsdk.interop.openqasm import from_openqasm, to_openqasm

        c = Circuit(2).crz(0, 1, math.pi / 2)
        qasm = to_openqasm(c)
        assert "crz(" in qasm
        c2 = from_openqasm(qasm)
        assert c2.gates[0].name == "CRZ"

    def test_ccz_roundtrip(self):
        from quantsdk.interop.openqasm import from_openqasm, to_openqasm

        c = Circuit(3).ccz(0, 1, 2)
        qasm = to_openqasm(c)
        assert "ccz" in qasm
        c2 = from_openqasm(qasm)
        assert c2.gates[0].name == "CCZ"

    def test_reset_roundtrip(self):
        from quantsdk.interop.openqasm import from_openqasm, to_openqasm

        c = Circuit(1)
        c.x(0)
        c.reset(0)
        qasm = to_openqasm(c)
        assert "reset" in qasm
        c2 = from_openqasm(qasm)
        assert any(g.name == "RESET" for g in c2.gates)

    def test_iswap_roundtrip(self):
        from quantsdk.interop.openqasm import from_openqasm, to_openqasm

        c = Circuit(2).iswap(0, 1)
        qasm = to_openqasm(c)
        assert "iswap" in qasm
        c2 = from_openqasm(qasm)
        assert c2.gates[0].name == "iSWAP"

    def test_complex_circuit_roundtrip(self):
        """Test a circuit with many new gates round-trips through OpenQASM."""
        from quantsdk.interop.openqasm import from_openqasm, to_openqasm

        c = Circuit(3)
        c.sdg(0).tdg(1).sx(0).p(0, 0.5)
        c.cy(0, 1).crx(0, 1, 0.7)
        c.ccz(0, 1, 2)
        c.measure_all()
        qasm = to_openqasm(c)
        c2 = from_openqasm(qasm)
        assert len(c2.gates) == len(c.gates)
