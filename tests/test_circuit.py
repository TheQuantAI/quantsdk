# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for the Circuit class — the core abstraction of QuantSDK."""

import math

import pytest

from quantsdk.circuit import Circuit


class TestCircuitCreation:
    """Test circuit initialization."""

    def test_create_simple_circuit(self):
        c = Circuit(2, name="test")
        assert c.num_qubits == 2
        assert c.name == "test"
        assert len(c) == 0
        assert c.depth == 0

    def test_create_circuit_default_name(self):
        c = Circuit(3)
        assert c.name == "circuit"

    def test_create_circuit_zero_qubits_raises(self):
        with pytest.raises(ValueError, match="positive"):
            Circuit(0)

    def test_create_circuit_negative_qubits_raises(self):
        with pytest.raises(ValueError, match="positive"):
            Circuit(-1)


class TestSingleQubitGates:
    """Test single-qubit gate operations."""

    def test_hadamard(self):
        c = Circuit(1)
        c.h(0)
        assert len(c) == 1
        assert c.gates[0].name == "H"
        assert c.gates[0].qubits == (0,)

    def test_pauli_gates(self):
        c = Circuit(1)
        c.x(0).y(0).z(0)
        assert len(c) == 3
        assert [g.name for g in c.gates] == ["X", "Y", "Z"]

    def test_s_and_t_gates(self):
        c = Circuit(1)
        c.s(0).t(0)
        assert [g.name for g in c.gates] == ["S", "T"]

    def test_identity_gate(self):
        c = Circuit(1)
        c.i(0)
        assert c.gates[0].name == "I"

    def test_qubit_out_of_range_raises(self):
        c = Circuit(2)
        with pytest.raises(IndexError, match="out of range"):
            c.h(2)

    def test_negative_qubit_raises(self):
        c = Circuit(2)
        with pytest.raises(IndexError, match="out of range"):
            c.h(-1)


class TestParametricGates:
    """Test parametric (rotation) gates."""

    def test_rx_gate(self):
        c = Circuit(1)
        c.rx(0, math.pi / 2)
        gate = c.gates[0]
        assert gate.name == "RX"
        assert gate.params == (math.pi / 2,)

    def test_ry_gate(self):
        c = Circuit(1)
        c.ry(0, math.pi)
        gate = c.gates[0]
        assert gate.name == "RY"
        assert gate.params == (math.pi,)

    def test_rz_gate(self):
        c = Circuit(1)
        c.rz(0, 0.5)
        assert c.gates[0].name == "RZ"
        assert c.gates[0].params == (0.5,)

    def test_u3_gate(self):
        c = Circuit(1)
        c.u3(0, math.pi, math.pi / 2, math.pi / 4)
        gate = c.gates[0]
        assert gate.name == "U3"
        assert gate.params == (math.pi, math.pi / 2, math.pi / 4)


class TestTwoQubitGates:
    """Test two-qubit gate operations."""

    def test_cx_gate(self):
        c = Circuit(2)
        c.cx(0, 1)
        gate = c.gates[0]
        assert gate.name == "CX"
        assert gate.qubits == (0, 1)

    def test_cnot_alias(self):
        c = Circuit(2)
        c.cnot(0, 1)
        assert c.gates[0].name == "CX"

    def test_cz_gate(self):
        c = Circuit(2)
        c.cz(0, 1)
        assert c.gates[0].name == "CZ"

    def test_swap_gate(self):
        c = Circuit(2)
        c.swap(0, 1)
        assert c.gates[0].name == "SWAP"

    def test_rzz_gate(self):
        c = Circuit(2)
        c.rzz(0, 1, math.pi / 4)
        gate = c.gates[0]
        assert gate.name == "RZZ"
        assert gate.params == (math.pi / 4,)

    def test_same_qubit_raises(self):
        c = Circuit(2)
        with pytest.raises(ValueError, match="Duplicate"):
            c.cx(0, 0)


class TestThreeQubitGates:
    """Test three-qubit gate operations."""

    def test_toffoli(self):
        c = Circuit(3)
        c.ccx(0, 1, 2)
        gate = c.gates[0]
        assert gate.name == "CCX"
        assert gate.qubits == (0, 1, 2)

    def test_toffoli_alias(self):
        c = Circuit(3)
        c.toffoli(0, 1, 2)
        assert c.gates[0].name == "CCX"

    def test_fredkin(self):
        c = Circuit(3)
        c.cswap(0, 1, 2)
        assert c.gates[0].name == "CSWAP"

    def test_fredkin_alias(self):
        c = Circuit(3)
        c.fredkin(0, 1, 2)
        assert c.gates[0].name == "CSWAP"


class TestMeasurement:
    """Test measurement operations."""

    def test_measure_single_qubit(self):
        c = Circuit(2)
        c.measure(0)
        assert c.num_measurements == 1

    def test_measure_all(self):
        c = Circuit(3)
        c.measure_all()
        assert c.num_measurements == 3

    def test_measure_out_of_range_raises(self):
        c = Circuit(2)
        with pytest.raises(IndexError):
            c.measure(2)


class TestCircuitProperties:
    """Test circuit analysis properties."""

    def test_depth_empty(self):
        c = Circuit(2)
        assert c.depth == 0

    def test_depth_single_gate(self):
        c = Circuit(2)
        c.h(0)
        assert c.depth == 1

    def test_depth_parallel_gates(self):
        c = Circuit(2)
        c.h(0)
        c.x(1)  # This can run in parallel with H on qubit 0
        assert c.depth == 1

    def test_depth_sequential_gates(self):
        c = Circuit(1)
        c.h(0)
        c.x(0)
        c.z(0)
        assert c.depth == 3

    def test_depth_bell_state(self):
        c = Circuit(2)
        c.h(0)
        c.cx(0, 1)
        assert c.depth == 2

    def test_gate_count_excludes_measurements(self):
        c = Circuit(2)
        c.h(0)
        c.cx(0, 1)
        c.measure_all()
        assert c.gate_count == 2

    def test_count_ops(self):
        c = Circuit(2)
        c.h(0).h(1).cx(0, 1).measure_all()
        ops = c.count_ops()
        assert ops["H"] == 2
        assert ops["CX"] == 1
        assert ops["MEASURE"] == 2

    def test_copy(self):
        c = Circuit(2, name="original")
        c.h(0).cx(0, 1)
        c2 = c.copy()
        assert c2.num_qubits == 2
        assert c2.name == "original"
        assert len(c2) == 2
        # Modifying copy doesn't affect original
        c2.x(0)
        assert len(c) == 2
        assert len(c2) == 3


class TestCircuitChaining:
    """Test that gate methods return self for fluent chaining."""

    def test_chain_single_qubit_gates(self):
        c = Circuit(1)
        result = c.h(0).x(0).y(0).z(0)
        assert result is c
        assert len(c) == 4

    def test_chain_mixed_gates(self):
        c = Circuit(3)
        c.h(0).cx(0, 1).ccx(0, 1, 2).measure_all()
        assert len(c) == 6  # 3 gates + 3 measurements


class TestCircuitDraw:
    """Test ASCII circuit drawing."""

    def test_draw_empty(self):
        c = Circuit(2)
        output = c.draw()
        assert "q0:" in output
        assert "q1:" in output

    def test_draw_bell_state(self):
        c = Circuit(2)
        c.h(0).cx(0, 1).measure_all()
        output = c.draw()
        assert "H" in output
        assert "●" in output
        assert "X" in output
        assert "M" in output

    def test_str_uses_draw(self):
        c = Circuit(2)
        c.h(0)
        assert str(c) == c.draw()

    def test_repr(self):
        c = Circuit(2, name="test")
        c.h(0)
        r = repr(c)
        assert "num_qubits=2" in r
        assert "test" in r
        assert "gates=1" in r
