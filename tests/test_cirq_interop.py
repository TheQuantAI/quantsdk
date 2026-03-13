# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for quantsdk.interop.cirq_interop — Cirq conversion."""

from __future__ import annotations

import math

import pytest

from quantsdk.circuit import Circuit
from quantsdk.gates import (
    CCZGate,
    CHGate,
    CPhaseGate,
    CRXGate,
    CRYGate,
    CRZGate,
    CSdgGate,
    CSGate,
    CSXGate,
    CXGate,
    CYGate,
    CZGate,
    FredkinGate,
    HGate,
    IGate,
    Measure,
    PhaseGate,
    RXGate,
    RXXGate,
    RYGate,
    RYYGate,
    RZGate,
    RZZGate,
    SdgGate,
    SGate,
    SwapGate,
    SXGate,
    TdgGate,
    TGate,
    ToffoliGate,
    XGate,
    YGate,
    ZGate,
    iSwapGate,
)

cirq = pytest.importorskip("cirq", reason="Cirq not installed")

from quantsdk.interop.cirq_interop import from_cirq, to_cirq  # noqa: E402, I001


# ─── to_cirq tests ───


class TestToCirq:
    """Test QuantSDK → Cirq conversion."""

    def test_bell_state(self) -> None:
        """Convert a Bell state circuit."""
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        cc = to_cirq(c)

        assert len(list(cc.all_qubits())) == 2

    def test_single_qubit_gates(self) -> None:
        """All single-qubit non-parametric gates convert."""
        c = Circuit(1)
        c.h(0).x(0).y(0).z(0).s(0).t(0).i(0)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 7

    def test_sdg_and_tdg(self) -> None:
        """S-dagger and T-dagger convert."""
        c = Circuit(1)
        c.sdg(0).tdg(0)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 2

    def test_sx_and_sxdg(self) -> None:
        """SX and SXdg gates convert."""
        c = Circuit(1)
        c.sx(0).sxdg(0)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 2

    def test_parametric_gates(self) -> None:
        """RX, RY, RZ with correct angles."""
        c = Circuit(1)
        c.rx(0, math.pi / 4).ry(0, math.pi / 3).rz(0, math.pi / 2)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 3

    def test_phase_gate(self) -> None:
        """Phase gate converts."""
        c = Circuit(1)
        c.p(0, math.pi / 4)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 1

    def test_u1_gate(self) -> None:
        """U1 gate converts."""
        c = Circuit(1)
        c.u1(0, math.pi / 4)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_u2_gate(self) -> None:
        """U2 gate converts via MatrixGate."""
        c = Circuit(1)
        c.u2(0, 0.5, 0.7)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_u3_gate(self) -> None:
        """U3 gate converts via MatrixGate."""
        c = Circuit(1)
        c.u3(0, 1.0, 2.0, 3.0)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_r_gate(self) -> None:
        """R gate converts via MatrixGate."""
        c = Circuit(1)
        c.r(0, math.pi / 3, math.pi / 4)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_two_qubit_gates(self) -> None:
        """CX, CZ, SWAP convert."""
        c = Circuit(2)
        c.cx(0, 1).cz(0, 1).swap(0, 1)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 3

    def test_cy_gate(self) -> None:
        """CY gate converts."""
        c = Circuit(2)
        c.cy(0, 1)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_ch_gate(self) -> None:
        """CH gate converts."""
        c = Circuit(2)
        c.ch(0, 1)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_iswap_gate(self) -> None:
        """iSWAP gate converts."""
        c = Circuit(2)
        c.iswap(0, 1)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_cs_csdg_gates(self) -> None:
        """CS and CSdg gates convert."""
        c = Circuit(2)
        c.cs(0, 1).csdg(0, 1)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 2

    def test_csx_gate(self) -> None:
        """CSX gate converts."""
        c = Circuit(2)
        c.csx(0, 1)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_controlled_rotation_gates(self) -> None:
        """CRX, CRY, CRZ convert."""
        c = Circuit(2)
        c.crx(0, 1, math.pi / 4).cry(0, 1, math.pi / 3).crz(0, 1, math.pi / 2)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 3

    def test_cphase_gate(self) -> None:
        """CPhase gate converts."""
        c = Circuit(2)
        c.cp(0, 1, math.pi / 4)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_cu1_gate(self) -> None:
        """CU1 gate converts."""
        c = Circuit(2)
        c.cu1(0, 1, math.pi / 4)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_cu3_gate(self) -> None:
        """CU3 gate converts via MatrixGate."""
        c = Circuit(2)
        c.cu3(0, 1, 1.0, 2.0, 3.0)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_rxx_ryy_rzz_gates(self) -> None:
        """RXX, RYY, RZZ convert."""
        c = Circuit(2)
        c.rxx(0, 1, math.pi / 4).ryy(0, 1, math.pi / 3).rzz(0, 1, math.pi / 2)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 3

    def test_rzx_gate(self) -> None:
        """RZX converts via MatrixGate."""
        c = Circuit(2)
        c.rzx(0, 1, math.pi / 4)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_dcx_gate(self) -> None:
        """DCX converts via MatrixGate."""
        c = Circuit(2)
        c.dcx(0, 1)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_ecr_gate(self) -> None:
        """ECR converts via MatrixGate."""
        c = Circuit(2)
        c.ecr(0, 1)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_three_qubit_gates(self) -> None:
        """Toffoli, CCZ, Fredkin convert."""
        c = Circuit(3)
        c.ccx(0, 1, 2).ccz(0, 1, 2).cswap(0, 1, 2)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 3

    def test_barrier_is_skipped(self) -> None:
        """Barriers have no Cirq equivalent and are skipped."""
        c = Circuit(2)
        c.h(0).barrier([0, 1]).cx(0, 1)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 2  # h + cx, barrier skipped

    def test_reset(self) -> None:
        """Reset converts to ResetChannel."""
        c = Circuit(1)
        c.reset(0)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 1

    def test_empty_circuit(self) -> None:
        """Empty circuit converts."""
        c = Circuit(3)
        cc = to_cirq(c)
        assert len(list(cc.all_operations())) == 0

    def test_measurements_create_keys(self) -> None:
        """Each measurement gets a unique key."""
        c = Circuit(2)
        c.measure(0).measure(1)
        cc = to_cirq(c)

        ops = list(cc.all_operations())
        assert len(ops) == 2

    def test_unsupported_gate_raises(self) -> None:
        """Unsupported gate type raises ValueError."""
        from quantsdk.gates import Gate

        c = Circuit(1)
        c._gates.append(Gate(name="UNSUPPORTED", qubits=(0,)))
        with pytest.raises(ValueError, match="Unsupported gate for Cirq export"):
            to_cirq(c)


# ─── from_cirq tests ───


class TestFromCirq:
    """Test Cirq → QuantSDK conversion."""

    def test_bell_state(self) -> None:
        """Import a Bell state from Cirq."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.H(q[0]),
            cirq.CNOT(q[0], q[1]),
            cirq.measure(q[0], q[1], key="result"),
        ])

        c = from_cirq(cc)
        assert c.num_qubits == 2
        assert isinstance(c.gates[0], HGate)
        assert isinstance(c.gates[1], CXGate)
        # 2 qubits measured → 2 Measure gates
        assert isinstance(c.gates[2], Measure)
        assert isinstance(c.gates[3], Measure)

    def test_single_qubit_gates(self) -> None:
        """Standard single-qubit gates import correctly."""
        q = cirq.LineQubit.range(1)
        cc = cirq.Circuit([
            cirq.H(q[0]),
            cirq.X(q[0]),
            cirq.Y(q[0]),
            cirq.Z(q[0]),
            cirq.S(q[0]),
            cirq.T(q[0]),
            cirq.I(q[0]),
        ])

        c = from_cirq(cc)
        gate_types = [type(g) for g in c.gates]
        assert gate_types == [HGate, XGate, YGate, ZGate, SGate, TGate, IGate]

    def test_sdg_and_tdg(self) -> None:
        """S-dagger and T-dagger import."""
        q = cirq.LineQubit.range(1)
        cc = cirq.Circuit([
            (cirq.S**-1)(q[0]),
            (cirq.T**-1)(q[0]),
        ])

        c = from_cirq(cc)
        assert isinstance(c.gates[0], SdgGate)
        assert isinstance(c.gates[1], TdgGate)

    def test_sx_gate(self) -> None:
        """SX gate (XPowGate exponent=0.5)."""
        q = cirq.LineQubit.range(1)
        cc = cirq.Circuit([
            cirq.XPowGate(exponent=0.5)(q[0]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], SXGate)

    def test_parametric_gates(self) -> None:
        """RX, RY, RZ import with correct angles."""
        q = cirq.LineQubit.range(1)
        cc = cirq.Circuit([
            cirq.rx(math.pi / 4)(q[0]),
            cirq.ry(math.pi / 3)(q[0]),
            cirq.rz(math.pi / 2)(q[0]),
        ])

        c = from_cirq(cc)
        assert isinstance(c.gates[0], RXGate)
        assert c.gates[0].params[0] == pytest.approx(math.pi / 4)
        assert isinstance(c.gates[1], RYGate)
        assert c.gates[1].params[0] == pytest.approx(math.pi / 3)
        assert isinstance(c.gates[2], RZGate)
        assert c.gates[2].params[0] == pytest.approx(math.pi / 2)

    def test_phase_gate_import(self) -> None:
        """General ZPowGate imports as PhaseGate."""
        q = cirq.LineQubit.range(1)
        cc = cirq.Circuit([
            cirq.ZPowGate(exponent=0.3)(q[0]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], PhaseGate)
        assert c.gates[0].params[0] == pytest.approx(0.3 * math.pi)

    def test_two_qubit_gates(self) -> None:
        """CX, CZ, SWAP import."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.CNOT(q[0], q[1]),
            cirq.CZ(q[0], q[1]),
            cirq.SWAP(q[0], q[1]),
        ])

        c = from_cirq(cc)
        gate_types = [type(g) for g in c.gates]
        assert gate_types == [CXGate, CZGate, SwapGate]

    def test_iswap(self) -> None:
        """iSWAP imports."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([cirq.ISWAP(q[0], q[1])])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], iSwapGate)

    def test_cz_pow_general(self) -> None:
        """Non-trivial CZPowGate imports as CPhaseGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([cirq.CZPowGate(exponent=0.3)(q[0], q[1])])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CPhaseGate)
        assert c.gates[0].params[0] == pytest.approx(0.3 * math.pi)

    def test_xx_yy_zz_pow(self) -> None:
        """XXPowGate, YYPowGate, ZZPowGate import as RXX, RYY, RZZ."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.XXPowGate(exponent=0.5)(q[0], q[1]),
            cirq.YYPowGate(exponent=0.3)(q[0], q[1]),
            cirq.ZZPowGate(exponent=0.7)(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], RXXGate)
        assert c.gates[0].params[0] == pytest.approx(0.5 * math.pi)
        assert isinstance(c.gates[1], RYYGate)
        assert c.gates[1].params[0] == pytest.approx(0.3 * math.pi)
        assert isinstance(c.gates[2], RZZGate)
        assert c.gates[2].params[0] == pytest.approx(0.7 * math.pi)

    def test_three_qubit_gates(self) -> None:
        """Toffoli, CCZ, Fredkin import."""
        q = cirq.LineQubit.range(3)
        cc = cirq.Circuit([
            cirq.TOFFOLI(q[0], q[1], q[2]),
            cirq.CCZ(q[0], q[1], q[2]),
            cirq.FREDKIN(q[0], q[1], q[2]),
        ])

        c = from_cirq(cc)
        assert isinstance(c.gates[0], ToffoliGate)
        assert isinstance(c.gates[1], CCZGate)
        assert isinstance(c.gates[2], FredkinGate)

    def test_controlled_h(self) -> None:
        """ControlledGate(H) imports as CHGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.ControlledGate(cirq.H)(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CHGate)

    def test_controlled_y(self) -> None:
        """ControlledGate(Y) imports as CYGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.ControlledGate(cirq.Y)(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CYGate)

    def test_controlled_s(self) -> None:
        """ControlledGate(S) imports as CSGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.ControlledGate(cirq.S)(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CSGate)

    def test_controlled_sdg(self) -> None:
        """ControlledGate(S**-1) imports as CSdgGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.ControlledGate(cirq.S**-1)(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CSdgGate)

    def test_controlled_rx(self) -> None:
        """ControlledGate(rx) imports as CRXGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.ControlledGate(cirq.rx(math.pi / 4))(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CRXGate)
        assert c.gates[0].params[0] == pytest.approx(math.pi / 4)

    def test_controlled_ry(self) -> None:
        """ControlledGate(ry) imports as CRYGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.ControlledGate(cirq.ry(math.pi / 3))(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CRYGate)
        assert c.gates[0].params[0] == pytest.approx(math.pi / 3)

    def test_controlled_rz(self) -> None:
        """ControlledGate(rz) imports as CRZGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.ControlledGate(cirq.rz(math.pi / 2))(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CRZGate)
        assert c.gates[0].params[0] == pytest.approx(math.pi / 2)

    def test_controlled_sx(self) -> None:
        """ControlledGate(XPowGate(0.5)) imports as CSXGate."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([
            cirq.ControlledGate(cirq.XPowGate(exponent=0.5))(q[0], q[1]),
        ])
        c = from_cirq(cc)
        assert isinstance(c.gates[0], CSXGate)

    def test_reset_import(self) -> None:
        """ResetChannel imports as Reset."""
        q = cirq.LineQubit.range(1)
        cc = cirq.Circuit([cirq.ResetChannel()(q[0])])
        c = from_cirq(cc)
        assert c.gates[0].name == "RESET"

    def test_empty_circuit(self) -> None:
        """Empty Cirq circuit."""
        cc = cirq.Circuit()
        c = from_cirq(cc)
        assert c.num_qubits >= 1

    def test_qubit_index_mapping(self) -> None:
        """Non-contiguous LineQubit indices are remapped."""
        q0, q2 = cirq.LineQubit(0), cirq.LineQubit(2)
        cc = cirq.Circuit([cirq.H(q0), cirq.CNOT(q0, q2)])
        c = from_cirq(cc)
        # q0 → 0, q2 → 1 (sorted order)
        assert c.num_qubits == 2
        assert c.gates[0].qubits == (0,)
        assert c.gates[1].qubits == (0, 1)

    def test_grid_qubit_mapping(self) -> None:
        """GridQubits are sorted and mapped to sequential indices."""
        q00, q01 = cirq.GridQubit(0, 0), cirq.GridQubit(0, 1)
        cc = cirq.Circuit([cirq.H(q00), cirq.CNOT(q00, q01)])
        c = from_cirq(cc)
        assert c.num_qubits == 2
        assert c.gates[0].qubits == (0,)
        assert c.gates[1].qubits == (0, 1)

    def test_unsupported_gate_raises(self) -> None:
        """Unsupported gate type raises ValueError."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([cirq.SwapPowGate(exponent=0.3)(q[0], q[1])])
        with pytest.raises(ValueError, match="Unsupported SwapPowGate"):
            from_cirq(cc)


# ─── Round-trip tests ───


class TestRoundTrip:
    """Test QuantSDK → Cirq → QuantSDK round-trips."""

    def test_roundtrip_bell_state(self) -> None:
        """Bell state survives round-trip."""
        original = Circuit(2).h(0).cx(0, 1).measure_all()
        cc = to_cirq(original)
        restored = from_cirq(cc)

        assert restored.num_qubits == 2
        assert isinstance(restored.gates[0], HGate)
        assert isinstance(restored.gates[1], CXGate)
        # Measurements
        assert sum(1 for g in restored.gates if isinstance(g, Measure)) == 2

    def test_roundtrip_single_qubit_non_parametric(self) -> None:
        """Non-parametric single-qubit gates survive round-trip."""
        original = Circuit(1)
        original.h(0).x(0).y(0).z(0).s(0).t(0).i(0)

        cc = to_cirq(original)
        restored = from_cirq(cc)

        assert len(restored.gates) == 7
        for orig, rest in zip(original.gates, restored.gates, strict=True):
            assert type(orig) is type(rest)

    def test_roundtrip_sdg_tdg(self) -> None:
        """Sdg and Tdg survive round-trip."""
        original = Circuit(1)
        original.sdg(0).tdg(0)

        cc = to_cirq(original)
        restored = from_cirq(cc)

        assert isinstance(restored.gates[0], SdgGate)
        assert isinstance(restored.gates[1], TdgGate)

    def test_roundtrip_parametric(self) -> None:
        """Parametric gates preserve angles through round-trip."""
        original = Circuit(2)
        original.rx(0, math.pi / 4).ry(1, math.pi / 3).cx(0, 1)

        cc = to_cirq(original)
        restored = from_cirq(cc)

        assert len(restored.gates) == 3
        assert restored.gates[0].params[0] == pytest.approx(math.pi / 4)
        assert restored.gates[1].params[0] == pytest.approx(math.pi / 3)

    def test_roundtrip_two_qubit(self) -> None:
        """Two-qubit gates survive round-trip."""
        original = Circuit(2)
        original.cx(0, 1).cz(0, 1).swap(0, 1).iswap(0, 1)

        cc = to_cirq(original)
        restored = from_cirq(cc)

        gate_types = [type(g) for g in restored.gates]
        assert gate_types == [CXGate, CZGate, SwapGate, iSwapGate]

    def test_roundtrip_three_qubit(self) -> None:
        """Three-qubit gates survive round-trip."""
        original = Circuit(3)
        original.ccx(0, 1, 2).ccz(0, 1, 2).cswap(0, 1, 2)

        cc = to_cirq(original)
        restored = from_cirq(cc)

        assert isinstance(restored.gates[0], ToffoliGate)
        assert isinstance(restored.gates[1], CCZGate)
        assert isinstance(restored.gates[2], FredkinGate)

    def test_roundtrip_complex_circuit(self) -> None:
        """Complex multi-gate circuit round-trips."""
        original = Circuit(3, name="complex")
        original.h(0).cx(0, 1).rx(2, 0.5).cz(1, 2).swap(0, 2)
        original.ccx(0, 1, 2).measure_all()

        cc = to_cirq(original)
        restored = from_cirq(cc)

        assert restored.num_qubits == 3
        assert len(restored.gates) == len(original.gates)


# ─── Circuit class convenience method tests ───


class TestCircuitMethods:
    """Test Circuit.to_cirq() and Circuit.from_cirq()."""

    def test_to_cirq_method(self) -> None:
        """Circuit.to_cirq() works."""
        c = Circuit(2).h(0).cx(0, 1)
        cc = c.to_cirq()
        assert len(list(cc.all_operations())) == 2

    def test_from_cirq_method(self) -> None:
        """Circuit.from_cirq() works."""
        q = cirq.LineQubit.range(2)
        cc = cirq.Circuit([cirq.H(q[0]), cirq.CNOT(q[0], q[1])])
        c = Circuit.from_cirq(cc)
        assert isinstance(c.gates[0], HGate)
        assert isinstance(c.gates[1], CXGate)


# ─── Import error handling ───


class TestImportErrors:
    """Test import error handling."""

    def test_check_cirq_no_error(self) -> None:
        """No error when cirq is installed."""
        from quantsdk.interop.cirq_interop import _check_cirq

        _check_cirq()  # Should not raise
