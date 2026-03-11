# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for quantsdk.interop.qiskit_interop — Qiskit conversion."""

from __future__ import annotations

import math

import pytest

from quantsdk.circuit import Circuit
from quantsdk.gates import (
    CXGate,
    CZGate,
    FredkinGate,
    HGate,
    IGate,
    Measure,
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

qiskit = pytest.importorskip("qiskit", reason="Qiskit not installed")
from qiskit.circuit import QuantumCircuit as QiskitQC  # noqa: E402

from quantsdk.interop.qiskit_interop import from_qiskit, to_qiskit  # noqa: E402

# ─── to_qiskit tests ───


class TestToQiskit:
    """Test QuantSDK → Qiskit conversion."""

    def test_bell_state(self):
        """Convert a Bell state circuit."""
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        qc = to_qiskit(c)

        assert qc.num_qubits == 2
        assert qc.num_clbits == 2  # 2 measurements
        assert qc.name == "circuit"

    def test_single_qubit_gates(self):
        """All single-qubit non-parametric gates convert."""
        c = Circuit(1)
        c.h(0).x(0).y(0).z(0).s(0).t(0).i(0)
        qc = to_qiskit(c)

        ops = [inst.operation.name for inst in qc.data]
        assert ops == ["h", "x", "y", "z", "s", "t", "id"]

    def test_parametric_gates(self):
        """RX, RY, RZ, U3 with correct angles."""
        c = Circuit(1)
        c.rx(0, math.pi / 4).ry(0, math.pi / 3).rz(0, math.pi / 2)
        c.u3(0, 1.0, 2.0, 3.0)
        qc = to_qiskit(c)

        ops = [inst.operation.name for inst in qc.data]
        assert ops == ["rx", "ry", "rz", "u"]

        # Check parameters
        assert qc.data[0].operation.params[0] == pytest.approx(math.pi / 4)
        assert qc.data[1].operation.params[0] == pytest.approx(math.pi / 3)
        assert qc.data[2].operation.params[0] == pytest.approx(math.pi / 2)
        assert qc.data[3].operation.params == [
            pytest.approx(1.0),
            pytest.approx(2.0),
            pytest.approx(3.0),
        ]

    def test_two_qubit_gates(self):
        """CX, CZ, SWAP, RZZ convert correctly."""
        c = Circuit(2)
        c.cx(0, 1).cz(0, 1).swap(0, 1).rzz(0, 1, math.pi)
        qc = to_qiskit(c)

        ops = [inst.operation.name for inst in qc.data]
        assert ops == ["cx", "cz", "swap", "rzz"]

    def test_three_qubit_gates(self):
        """Toffoli and Fredkin convert."""
        c = Circuit(3)
        c.ccx(0, 1, 2).cswap(0, 1, 2)
        qc = to_qiskit(c)

        ops = [inst.operation.name for inst in qc.data]
        assert ops == ["ccx", "cswap"]

    def test_barrier(self):
        """Barrier is preserved."""
        c = Circuit(2)
        c.h(0).barrier([0, 1]).cx(0, 1)
        qc = to_qiskit(c)

        ops = [inst.operation.name for inst in qc.data]
        assert "barrier" in ops

    def test_empty_circuit(self):
        """Empty circuit converts to empty Qiskit circuit."""
        c = Circuit(3)
        qc = to_qiskit(c)
        assert qc.num_qubits == 3
        assert len(qc.data) == 0

    def test_measurements_add_classical_bits(self):
        """Measurements create classical bits."""
        c = Circuit(3)
        c.h(0).cx(0, 1).cx(1, 2)
        c.measure(0).measure(1).measure(2)
        qc = to_qiskit(c)

        assert qc.num_clbits == 3
        measure_ops = [inst for inst in qc.data if inst.operation.name == "measure"]
        assert len(measure_ops) == 3

    def test_circuit_name_preserved(self):
        """Circuit name is passed to Qiskit."""
        c = Circuit(2, name="my_test_circuit")
        qc = to_qiskit(c)
        assert qc.name == "my_test_circuit"


# ─── from_qiskit tests ───


class TestFromQiskit:
    """Test Qiskit → QuantSDK conversion."""

    def test_bell_state(self):
        """Import a Bell state from Qiskit."""
        qc = QiskitQC(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        c = from_qiskit(qc)
        assert c.num_qubits == 2
        assert len(c.gates) == 4  # h, cx, measure, measure

        assert isinstance(c.gates[0], HGate)
        assert isinstance(c.gates[1], CXGate)
        assert isinstance(c.gates[2], Measure)
        assert isinstance(c.gates[3], Measure)

    def test_single_qubit_gates(self):
        """All single-qubit gates import correctly."""
        qc = QiskitQC(1)
        qc.h(0)
        qc.x(0)
        qc.y(0)
        qc.z(0)
        qc.s(0)
        qc.t(0)
        qc.id(0)

        c = from_qiskit(qc)
        gate_types = [type(g) for g in c.gates]
        assert gate_types == [HGate, XGate, YGate, ZGate, SGate, TGate, IGate]

    def test_parametric_gates(self):
        """Parametric gates import with correct angles."""
        qc = QiskitQC(1)
        qc.rx(math.pi / 4, 0)
        qc.ry(math.pi / 3, 0)
        qc.rz(math.pi / 2, 0)
        qc.u(1.0, 2.0, 3.0, 0)

        c = from_qiskit(qc)
        assert isinstance(c.gates[0], RXGate)
        assert c.gates[0].params[0] == pytest.approx(math.pi / 4)
        assert isinstance(c.gates[1], RYGate)
        assert isinstance(c.gates[2], RZGate)
        assert isinstance(c.gates[3], U3Gate)
        assert c.gates[3].params == pytest.approx((1.0, 2.0, 3.0))

    def test_two_qubit_gates(self):
        """Two-qubit gates import."""
        qc = QiskitQC(2)
        qc.cx(0, 1)
        qc.cz(0, 1)
        qc.swap(0, 1)

        c = from_qiskit(qc)
        gate_types = [type(g) for g in c.gates]
        assert gate_types == [CXGate, CZGate, SwapGate]

    def test_three_qubit_gates(self):
        """Three-qubit gates import."""
        qc = QiskitQC(3)
        qc.ccx(0, 1, 2)
        qc.cswap(0, 1, 2)

        c = from_qiskit(qc)
        assert isinstance(c.gates[0], ToffoliGate)
        assert isinstance(c.gates[1], FredkinGate)

    def test_qubit_indices_preserved(self):
        """Qubit indices are correctly mapped."""
        qc = QiskitQC(3)
        qc.h(2)
        qc.cx(2, 0)

        c = from_qiskit(qc)
        assert c.gates[0].qubits == (2,)
        assert c.gates[1].qubits == (2, 0)


# ─── Round-trip tests ───


class TestRoundTrip:
    """Test QuantSDK → Qiskit → QuantSDK round-trips."""

    def test_roundtrip_bell_state(self):
        """Bell state survives round-trip conversion."""
        original = Circuit(2).h(0).cx(0, 1).measure_all()
        qc = to_qiskit(original)
        restored = from_qiskit(qc)

        assert restored.num_qubits == 2
        assert len(restored.gates) == len(original.gates)

        for orig, rest in zip(original.gates, restored.gates, strict=True):
            assert type(orig) is type(rest)
            assert orig.qubits == rest.qubits

    def test_roundtrip_parametric(self):
        """Parametric circuit survives round-trip."""
        original = Circuit(2)
        original.rx(0, math.pi / 4).ry(1, math.pi / 3).cx(0, 1)

        qc = to_qiskit(original)
        restored = from_qiskit(qc)

        assert len(restored.gates) == 3
        assert restored.gates[0].params[0] == pytest.approx(math.pi / 4)
        assert restored.gates[1].params[0] == pytest.approx(math.pi / 3)

    def test_roundtrip_all_single_qubit(self):
        """All single-qubit gates survive round-trip."""
        original = Circuit(1)
        original.h(0).x(0).y(0).z(0).s(0).t(0).i(0)

        qc = to_qiskit(original)
        restored = from_qiskit(qc)

        assert len(restored.gates) == 7
        for orig, rest in zip(original.gates, restored.gates, strict=True):
            assert type(orig) is type(rest)

    def test_roundtrip_complex_circuit(self):
        """Complex multi-gate circuit round-trips."""
        original = Circuit(3, name="complex")
        original.h(0).cx(0, 1).rx(2, 0.5).cz(1, 2).swap(0, 2)
        original.ccx(0, 1, 2).measure_all()

        qc = to_qiskit(original)
        restored = from_qiskit(qc)

        assert restored.num_qubits == 3
        assert len(restored.gates) == len(original.gates)
