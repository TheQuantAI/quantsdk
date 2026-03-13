# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for quantsdk.interop.pennylane_interop -- PennyLane conversion."""

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
    CXGate,
    CYGate,
    CZGate,
    ECRGate,
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
    U1Gate,
    U2Gate,
    U3Gate,
    XGate,
    YGate,
    ZGate,
    iSwapGate,
)

qml = pytest.importorskip("pennylane", reason="PennyLane not installed")

from quantsdk.interop.pennylane_interop import from_pennylane, to_pennylane  # noqa: E402, I001


# ─── Helper ───


def _make_tape(
    ops: list[object], measurements: list[object] | None = None
) -> qml.tape.QuantumScript:
    """Create a PennyLane tape from operations and measurements."""
    if measurements is None:
        wires = set()
        for op in ops:
            wires.update(op.wires.tolist())  # type: ignore[union-attr]
        measurements = [qml.counts(wires=sorted(wires))] if wires else []
    return qml.tape.QuantumScript(ops, measurements)  # type: ignore[arg-type]


# ─── to_pennylane tests ───


class TestToPennylane:
    """Test QuantSDK -> PennyLane conversion."""

    def test_bell_state(self) -> None:
        """Convert a Bell state circuit."""
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        tape = to_pennylane(c)

        op_names = [op.name for op in tape.operations]
        assert "Hadamard" in op_names
        assert "CNOT" in op_names

    def test_single_qubit_gates(self) -> None:
        """All non-parametric single-qubit gates convert."""
        c = Circuit(1)
        c.h(0).x(0).y(0).z(0).s(0).t(0).i(0)
        tape = to_pennylane(c)
        assert len(tape.operations) == 7

    def test_sdg_and_tdg(self) -> None:
        """S-dagger and T-dagger convert as Adjoint."""
        c = Circuit(1)
        c.sdg(0).tdg(0)
        tape = to_pennylane(c)
        assert len(tape.operations) == 2
        assert "Adjoint(S)" in tape.operations[0].name
        assert "Adjoint(T)" in tape.operations[1].name

    def test_sx_gate(self) -> None:
        """SX gate converts."""
        c = Circuit(1)
        c.sx(0)
        tape = to_pennylane(c)
        assert len(tape.operations) == 1
        assert tape.operations[0].name == "SX"

    def test_parametric_gates(self) -> None:
        """RX, RY, RZ convert with correct angles."""
        c = Circuit(1)
        c.rx(0, math.pi / 4).ry(0, math.pi / 3).rz(0, math.pi / 2)
        tape = to_pennylane(c)

        assert len(tape.operations) == 3
        assert tape.operations[0].parameters[0] == pytest.approx(math.pi / 4)
        assert tape.operations[1].parameters[0] == pytest.approx(math.pi / 3)
        assert tape.operations[2].parameters[0] == pytest.approx(math.pi / 2)

    def test_phase_gate(self) -> None:
        """Phase gate converts to PhaseShift."""
        c = Circuit(1)
        c.p(0, math.pi / 4)
        tape = to_pennylane(c)
        assert tape.operations[0].name == "PhaseShift"
        assert tape.operations[0].parameters[0] == pytest.approx(math.pi / 4)

    def test_u1_gate(self) -> None:
        """U1 converts."""
        c = Circuit(1)
        c.u1(0, 0.5)
        tape = to_pennylane(c)
        assert tape.operations[0].name == "U1"

    def test_u2_gate(self) -> None:
        """U2 converts."""
        c = Circuit(1)
        c.u2(0, 0.5, 0.7)
        tape = to_pennylane(c)
        assert tape.operations[0].name == "U2"

    def test_u3_gate(self) -> None:
        """U3 converts."""
        c = Circuit(1)
        c.u3(0, 1.0, 2.0, 3.0)
        tape = to_pennylane(c)
        assert tape.operations[0].name == "U3"
        assert len(tape.operations[0].parameters) == 3

    def test_two_qubit_gates(self) -> None:
        """CX, CZ, SWAP convert."""
        c = Circuit(2)
        c.cx(0, 1).cz(0, 1).swap(0, 1)
        tape = to_pennylane(c)
        op_names = [op.name for op in tape.operations]
        assert op_names == ["CNOT", "CZ", "SWAP"]

    def test_cy_ch_gates(self) -> None:
        """CY and CH convert."""
        c = Circuit(2)
        c.cy(0, 1).ch(0, 1)
        tape = to_pennylane(c)
        op_names = [op.name for op in tape.operations]
        assert op_names == ["CY", "CH"]

    def test_iswap_gate(self) -> None:
        """iSWAP converts."""
        c = Circuit(2)
        c.iswap(0, 1)
        tape = to_pennylane(c)
        assert tape.operations[0].name == "ISWAP"

    def test_ecr_gate(self) -> None:
        """ECR converts."""
        c = Circuit(2)
        c.ecr(0, 1)
        tape = to_pennylane(c)
        assert tape.operations[0].name == "ECR"

    def test_controlled_rotation_gates(self) -> None:
        """CRX, CRY, CRZ convert."""
        c = Circuit(2)
        c.crx(0, 1, math.pi / 4).cry(0, 1, math.pi / 3).crz(0, 1, math.pi / 2)
        tape = to_pennylane(c)
        op_names = [op.name for op in tape.operations]
        assert op_names == ["CRX", "CRY", "CRZ"]

    def test_cphase_gate(self) -> None:
        """CPhase converts to ControlledPhaseShift."""
        c = Circuit(2)
        c.cp(0, 1, math.pi / 4)
        tape = to_pennylane(c)
        assert tape.operations[0].name == "ControlledPhaseShift"

    def test_ising_gates(self) -> None:
        """RXX, RYY, RZZ convert to IsingXX, IsingYY, IsingZZ."""
        c = Circuit(2)
        c.rxx(0, 1, 0.5).ryy(0, 1, 0.3).rzz(0, 1, 0.7)
        tape = to_pennylane(c)
        op_names = [op.name for op in tape.operations]
        assert op_names == ["IsingXX", "IsingYY", "IsingZZ"]

    def test_three_qubit_gates(self) -> None:
        """Toffoli, CSWAP, CCZ convert."""
        c = Circuit(3)
        c.ccx(0, 1, 2).cswap(0, 1, 2).ccz(0, 1, 2)
        tape = to_pennylane(c)
        op_names = [op.name for op in tape.operations]
        assert op_names == ["Toffoli", "CSWAP", "CCZ"]

    def test_barrier_converts(self) -> None:
        """Barrier converts to PennyLane Barrier."""
        c = Circuit(2)
        c.h(0).barrier([0, 1]).cx(0, 1)
        tape = to_pennylane(c)
        op_names = [op.name for op in tape.operations]
        assert "Barrier" in op_names

    def test_empty_circuit(self) -> None:
        """Empty circuit produces tape with no gate operations."""
        c = Circuit(2)
        tape = to_pennylane(c)
        assert len(tape.operations) == 0

    def test_measurements_produce_counts(self) -> None:
        """Circuit with measurements produces counts measurement."""
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        tape = to_pennylane(c)
        assert len(tape.measurements) == 1

    def test_no_measurements_produce_state(self) -> None:
        """Circuit without measurements produces state measurement."""
        c = Circuit(2).h(0).cx(0, 1)
        tape = to_pennylane(c)
        assert len(tape.measurements) == 1

    def test_unsupported_gate_raises(self) -> None:
        """Unsupported gate raises ValueError."""
        from quantsdk.gates import Gate

        c = Circuit(1)
        c._gates.append(Gate(name="UNSUPPORTED", qubits=(0,)))
        with pytest.raises(ValueError, match="Unsupported gate for PennyLane"):
            to_pennylane(c)


# ─── from_pennylane tests ───


class TestFromPennylane:
    """Test PennyLane -> QuantSDK conversion."""

    def test_bell_state(self) -> None:
        """Import a Bell state from PennyLane."""
        tape = _make_tape(
            [
                qml.Hadamard(wires=0),
                qml.CNOT(wires=[0, 1]),
            ]
        )
        c = from_pennylane(tape)
        assert c.num_qubits == 2
        assert isinstance(c.gates[0], HGate)
        assert isinstance(c.gates[1], CXGate)

    def test_single_qubit_gates(self) -> None:
        """Standard single-qubit gates import."""
        tape = _make_tape(
            [
                qml.Hadamard(wires=0),
                qml.PauliX(wires=0),
                qml.PauliY(wires=0),
                qml.PauliZ(wires=0),
                qml.S(wires=0),
                qml.T(wires=0),
                qml.Identity(wires=0),
            ]
        )
        c = from_pennylane(tape)
        gate_types = [type(g) for g in c.gates if not isinstance(g, Measure)]
        assert gate_types == [HGate, XGate, YGate, ZGate, SGate, TGate, IGate]

    def test_sx_gate(self) -> None:
        """SX imports."""
        tape = _make_tape([qml.SX(wires=0)])
        c = from_pennylane(tape)
        assert isinstance(c.gates[0], SXGate)

    def test_adjoint_s_and_t(self) -> None:
        """Adjoint(S) -> SdgGate, Adjoint(T) -> TdgGate."""
        tape = _make_tape(
            [
                qml.adjoint(qml.S(wires=0)),
                qml.adjoint(qml.T(wires=0)),
            ]
        )
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], SdgGate)
        assert isinstance(non_meas[1], TdgGate)

    def test_adjoint_sx(self) -> None:
        """Adjoint(SX) -> SXdgGate."""
        tape = _make_tape([qml.adjoint(qml.SX(wires=0))])
        c = from_pennylane(tape)
        from quantsdk.gates import SXdgGate

        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], SXdgGate)

    def test_parametric_gates(self) -> None:
        """RX, RY, RZ import with correct angles."""
        tape = _make_tape(
            [
                qml.RX(math.pi / 4, wires=0),
                qml.RY(math.pi / 3, wires=0),
                qml.RZ(math.pi / 2, wires=0),
            ]
        )
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], RXGate)
        assert non_meas[0].params[0] == pytest.approx(math.pi / 4)
        assert isinstance(non_meas[1], RYGate)
        assert isinstance(non_meas[2], RZGate)

    def test_phase_shift(self) -> None:
        """PhaseShift imports as PhaseGate."""
        tape = _make_tape([qml.PhaseShift(0.5, wires=0)])
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], PhaseGate)
        assert non_meas[0].params[0] == pytest.approx(0.5)

    def test_u1_u2_u3(self) -> None:
        """U1, U2, U3 import."""
        tape = _make_tape(
            [
                qml.U1(0.5, wires=0),
                qml.U2(0.5, 0.7, wires=0),
                qml.U3(1.0, 2.0, 3.0, wires=0),
            ]
        )
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], U1Gate)
        assert isinstance(non_meas[1], U2Gate)
        assert isinstance(non_meas[2], U3Gate)
        assert non_meas[2].params == pytest.approx((1.0, 2.0, 3.0))

    def test_two_qubit_gates(self) -> None:
        """CX, CZ, SWAP import."""
        tape = _make_tape(
            [
                qml.CNOT(wires=[0, 1]),
                qml.CZ(wires=[0, 1]),
                qml.SWAP(wires=[0, 1]),
            ]
        )
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        gate_types = [type(g) for g in non_meas]
        assert gate_types == [CXGate, CZGate, SwapGate]

    def test_cy_ch(self) -> None:
        """CY, CH import."""
        tape = _make_tape(
            [
                qml.CY(wires=[0, 1]),
                qml.CH(wires=[0, 1]),
            ]
        )
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], CYGate)
        assert isinstance(non_meas[1], CHGate)

    def test_iswap(self) -> None:
        """iSWAP imports."""
        tape = _make_tape([qml.ISWAP(wires=[0, 1])])
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], iSwapGate)

    def test_ecr(self) -> None:
        """ECR imports."""
        tape = _make_tape([qml.ECR(wires=[0, 1])])
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], ECRGate)

    def test_controlled_rotations(self) -> None:
        """CRX, CRY, CRZ import."""
        tape = _make_tape(
            [
                qml.CRX(math.pi / 4, wires=[0, 1]),
                qml.CRY(math.pi / 3, wires=[0, 1]),
                qml.CRZ(math.pi / 2, wires=[0, 1]),
            ]
        )
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], CRXGate)
        assert non_meas[0].params[0] == pytest.approx(math.pi / 4)
        assert isinstance(non_meas[1], CRYGate)
        assert isinstance(non_meas[2], CRZGate)

    def test_controlled_phase_shift(self) -> None:
        """ControlledPhaseShift imports as CPhaseGate."""
        tape = _make_tape([qml.ControlledPhaseShift(0.5, wires=[0, 1])])
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], CPhaseGate)

    def test_ising_gates(self) -> None:
        """IsingXX, IsingYY, IsingZZ import as RXX, RYY, RZZ."""
        tape = _make_tape(
            [
                qml.IsingXX(0.5, wires=[0, 1]),
                qml.IsingYY(0.3, wires=[0, 1]),
                qml.IsingZZ(0.7, wires=[0, 1]),
            ]
        )
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], RXXGate)
        assert isinstance(non_meas[1], RYYGate)
        assert isinstance(non_meas[2], RZZGate)

    def test_three_qubit_gates(self) -> None:
        """Toffoli, CSWAP, CCZ import."""
        tape = _make_tape(
            [
                qml.Toffoli(wires=[0, 1, 2]),
                qml.CSWAP(wires=[0, 1, 2]),
                qml.CCZ(wires=[0, 1, 2]),
            ]
        )
        c = from_pennylane(tape)
        non_meas = [g for g in c.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], ToffoliGate)
        assert isinstance(non_meas[1], FredkinGate)
        assert isinstance(non_meas[2], CCZGate)

    def test_empty_tape(self) -> None:
        """Empty tape produces minimal circuit."""
        tape = qml.tape.QuantumScript([], [])
        c = from_pennylane(tape)
        assert c.num_qubits >= 1

    def test_wire_mapping(self) -> None:
        """Non-contiguous wires are remapped."""
        tape = _make_tape(
            [
                qml.Hadamard(wires=0),
                qml.CNOT(wires=[0, 5]),
            ]
        )
        c = from_pennylane(tape)
        assert c.num_qubits == 2  # wires 0, 5 -> indices 0, 1
        assert c.gates[0].qubits == (0,)
        assert c.gates[1].qubits == (0, 1)

    def test_measurements_added(self) -> None:
        """Tape measurements generate Measure gates."""
        tape = _make_tape(
            [qml.Hadamard(wires=0), qml.CNOT(wires=[0, 1])],
            [qml.counts(wires=[0, 1])],
        )
        c = from_pennylane(tape)
        measure_gates = [g for g in c.gates if isinstance(g, Measure)]
        assert len(measure_gates) == 2


# ─── Round-trip tests ───


class TestRoundTrip:
    """Test QuantSDK -> PennyLane -> QuantSDK round-trips."""

    def test_roundtrip_bell_state(self) -> None:
        """Bell state survives round-trip."""
        original = Circuit(2).h(0).cx(0, 1).measure_all()
        tape = to_pennylane(original)
        restored = from_pennylane(tape)

        assert restored.num_qubits == 2
        assert isinstance(restored.gates[0], HGate)
        assert isinstance(restored.gates[1], CXGate)

    def test_roundtrip_single_qubit(self) -> None:
        """Non-parametric single-qubit gates survive round-trip."""
        original = Circuit(1)
        original.h(0).x(0).y(0).z(0).s(0).t(0).i(0)
        original.measure(0)

        tape = to_pennylane(original)
        restored = from_pennylane(tape)

        non_meas_orig = [g for g in original.gates if not isinstance(g, Measure)]
        non_meas_rest = [g for g in restored.gates if not isinstance(g, Measure)]
        assert len(non_meas_rest) == len(non_meas_orig)
        for orig, rest in zip(non_meas_orig, non_meas_rest, strict=True):
            assert type(orig) is type(rest)

    def test_roundtrip_parametric(self) -> None:
        """Parametric gates preserve angles."""
        original = Circuit(2)
        original.rx(0, math.pi / 4).ry(1, math.pi / 3).cx(0, 1).measure_all()

        tape = to_pennylane(original)
        restored = from_pennylane(tape)

        non_meas = [g for g in restored.gates if not isinstance(g, Measure)]
        assert non_meas[0].params[0] == pytest.approx(math.pi / 4)
        assert non_meas[1].params[0] == pytest.approx(math.pi / 3)

    def test_roundtrip_two_qubit(self) -> None:
        """Two-qubit gates survive round-trip."""
        original = Circuit(2)
        original.cx(0, 1).cz(0, 1).swap(0, 1).iswap(0, 1).measure_all()

        tape = to_pennylane(original)
        restored = from_pennylane(tape)

        non_meas = [g for g in restored.gates if not isinstance(g, Measure)]
        gate_types = [type(g) for g in non_meas]
        assert gate_types == [CXGate, CZGate, SwapGate, iSwapGate]

    def test_roundtrip_three_qubit(self) -> None:
        """Three-qubit gates survive round-trip."""
        original = Circuit(3)
        original.ccx(0, 1, 2).cswap(0, 1, 2).ccz(0, 1, 2).measure_all()

        tape = to_pennylane(original)
        restored = from_pennylane(tape)

        non_meas = [g for g in restored.gates if not isinstance(g, Measure)]
        assert isinstance(non_meas[0], ToffoliGate)
        assert isinstance(non_meas[1], FredkinGate)
        assert isinstance(non_meas[2], CCZGate)


# ─── Circuit class convenience method tests ───


class TestCircuitMethods:
    """Test Circuit.to_pennylane() and Circuit.from_pennylane()."""

    def test_to_pennylane_method(self) -> None:
        """Circuit.to_pennylane() works."""
        c = Circuit(2).h(0).cx(0, 1)
        tape = c.to_pennylane()
        assert len(tape.operations) == 2

    def test_from_pennylane_method(self) -> None:
        """Circuit.from_pennylane() works."""
        tape = _make_tape([qml.Hadamard(wires=0), qml.CNOT(wires=[0, 1])])
        c = Circuit.from_pennylane(tape)
        assert isinstance(c.gates[0], HGate)
        assert isinstance(c.gates[1], CXGate)


# ─── Import error handling ───


class TestImportErrors:
    """Test import error handling."""

    def test_check_pennylane_no_error(self) -> None:
        """No error when PennyLane is installed."""
        from quantsdk.interop.pennylane_interop import _check_pennylane

        _check_pennylane()  # Should not raise
