# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for quantsdk.interop.openqasm — OpenQASM 2.0 export/import."""

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
from quantsdk.interop.openqasm import from_openqasm, to_openqasm

# ─── to_openqasm tests ───


class TestToOpenQASM:
    """Test QuantSDK → OpenQASM 2.0 export."""

    def test_header(self):
        """QASM output starts with correct header."""
        c = Circuit(2)
        qasm = to_openqasm(c)
        lines = qasm.strip().splitlines()
        assert lines[0] == "OPENQASM 2.0;"
        assert lines[1] == 'include "qelib1.inc";'

    def test_registers(self):
        """Correct qreg/creg declarations."""
        c = Circuit(3).measure_all()
        qasm = to_openqasm(c)
        assert "qreg q[3];" in qasm
        assert "creg c[3];" in qasm

    def test_no_creg_without_measurements(self):
        """No creg if no measurements."""
        c = Circuit(2).h(0).cx(0, 1)
        qasm = to_openqasm(c)
        assert "creg" not in qasm

    def test_bell_state(self):
        """Bell state exports correctly."""
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        qasm = to_openqasm(c)

        assert "h q[0];" in qasm
        assert "cx q[0],q[1];" in qasm
        assert "measure q[0] -> c[0];" in qasm
        assert "measure q[1] -> c[1];" in qasm

    def test_single_qubit_gates(self):
        """All single-qubit gates export."""
        c = Circuit(1)
        c.h(0).x(0).y(0).z(0).s(0).t(0).i(0)
        qasm = to_openqasm(c)

        assert "h q[0];" in qasm
        assert "x q[0];" in qasm
        assert "y q[0];" in qasm
        assert "z q[0];" in qasm
        assert "s q[0];" in qasm
        assert "t q[0];" in qasm
        assert "id q[0];" in qasm

    def test_parametric_gates(self):
        """Parametric gates include parameters."""
        c = Circuit(1)
        c.rx(0, 1.5).ry(0, 2.5).rz(0, 3.5)
        qasm = to_openqasm(c)

        assert "rx(1.5) q[0];" in qasm
        assert "ry(2.5) q[0];" in qasm
        assert "rz(3.5) q[0];" in qasm

    def test_u3_gate(self):
        """U3 gate exports with three parameters."""
        c = Circuit(1).u3(0, 1.0, 2.0, 3.0)
        qasm = to_openqasm(c)
        assert "u3(1.0,2.0,3.0) q[0];" in qasm

    def test_two_qubit_gates(self):
        """Two-qubit gates export correctly."""
        c = Circuit(2)
        c.cx(0, 1).cz(0, 1).swap(0, 1)
        qasm = to_openqasm(c)

        assert "cx q[0],q[1];" in qasm
        assert "cz q[0],q[1];" in qasm
        assert "swap q[0],q[1];" in qasm

    def test_three_qubit_gates(self):
        """Three-qubit gates export."""
        c = Circuit(3).ccx(0, 1, 2).cswap(0, 1, 2)
        qasm = to_openqasm(c)

        assert "ccx q[0],q[1],q[2];" in qasm
        assert "cswap q[0],q[1],q[2];" in qasm

    def test_barrier(self):
        """Barrier exports."""
        c = Circuit(2).h(0).barrier([0, 1]).cx(0, 1)
        qasm = to_openqasm(c)
        assert "barrier q[0],q[1];" in qasm

    def test_rzz_gate(self):
        """RZZ gate with parameter exports."""
        c = Circuit(2).rzz(0, 1, math.pi)
        qasm = to_openqasm(c)
        assert f"rzz({math.pi}) q[0],q[1];" in qasm


# ─── from_openqasm tests ───


class TestFromOpenQASM:
    """Test OpenQASM 2.0 → QuantSDK import."""

    def test_bell_state(self):
        """Parse Bell state QASM."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        creg c[2];
        h q[0];
        cx q[0],q[1];
        measure q[0] -> c[0];
        measure q[1] -> c[1];
        """
        c = from_openqasm(qasm)

        assert c.num_qubits == 2
        assert isinstance(c.gates[0], HGate)
        assert isinstance(c.gates[1], CXGate)
        assert isinstance(c.gates[2], Measure)
        assert isinstance(c.gates[3], Measure)

    def test_single_qubit_gates(self):
        """Parse single-qubit gate instructions."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[1];
        h q[0];
        x q[0];
        y q[0];
        z q[0];
        s q[0];
        t q[0];
        id q[0];
        """
        c = from_openqasm(qasm)
        types = [type(g) for g in c.gates]
        assert types == [HGate, XGate, YGate, ZGate, SGate, TGate, IGate]

    def test_parametric_gates(self):
        """Parse parametric gates with float values."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[1];
        rx(0.785) q[0];
        ry(1.047) q[0];
        rz(1.571) q[0];
        """
        c = from_openqasm(qasm)

        assert isinstance(c.gates[0], RXGate)
        assert c.gates[0].params[0] == pytest.approx(0.785)
        assert isinstance(c.gates[1], RYGate)
        assert isinstance(c.gates[2], RZGate)

    def test_u3_gate(self):
        """Parse U3 gate with three params."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[1];
        u3(1.0,2.0,3.0) q[0];
        """
        c = from_openqasm(qasm)
        assert isinstance(c.gates[0], U3Gate)
        assert c.gates[0].params == pytest.approx((1.0, 2.0, 3.0))

    def test_two_qubit_gates(self):
        """Parse two-qubit gates."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        cx q[0],q[1];
        cz q[0],q[1];
        swap q[0],q[1];
        """
        c = from_openqasm(qasm)
        types = [type(g) for g in c.gates]
        assert types == [CXGate, CZGate, SwapGate]

    def test_three_qubit_gates(self):
        """Parse three-qubit gates."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[3];
        ccx q[0],q[1],q[2];
        cswap q[0],q[1],q[2];
        """
        c = from_openqasm(qasm)
        assert isinstance(c.gates[0], ToffoliGate)
        assert isinstance(c.gates[1], FredkinGate)

    def test_barrier(self):
        """Parse barrier."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        h q[0];
        barrier q[0],q[1];
        cx q[0],q[1];
        """
        c = from_openqasm(qasm)
        from quantsdk.gates import Barrier

        assert len(c.gates) == 3
        assert isinstance(c.gates[1], Barrier)

    def test_comments_ignored(self):
        """Comments are skipped."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        // This is a comment
        qreg q[1];
        h q[0]; // inline comments won't be here
        """
        c = from_openqasm(qasm)
        assert len(c.gates) == 1

    def test_pi_parameter(self):
        """Parse pi-based parameter expressions."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[1];
        rx(pi/4) q[0];
        """
        c = from_openqasm(qasm)
        assert c.gates[0].params[0] == pytest.approx(math.pi / 4)

    def test_no_qreg_raises(self):
        """Missing qreg raises ValueError."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        h q[0];
        """
        with pytest.raises(ValueError, match="No qreg"):
            from_openqasm(qasm)

    def test_unsupported_gate_raises(self):
        """Unsupported gate raises ValueError."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[1];
        fake_gate q[0];
        """
        with pytest.raises(ValueError, match="Unsupported QASM gate"):
            from_openqasm(qasm)


# ─── Round-trip tests ───


class TestRoundTripQASM:
    """Test QuantSDK → QASM → QuantSDK round-trips."""

    def test_roundtrip_bell(self):
        """Bell state survives QASM round-trip."""
        original = Circuit(2).h(0).cx(0, 1).measure_all()
        qasm = to_openqasm(original)
        restored = from_openqasm(qasm)

        assert restored.num_qubits == 2
        assert len(restored.gates) == len(original.gates)
        for orig, rest in zip(original.gates, restored.gates, strict=True):
            assert type(orig) is type(rest)
            assert orig.qubits == rest.qubits

    def test_roundtrip_parametric(self):
        """Parametric circuit survives QASM round-trip."""
        original = Circuit(2)
        original.rx(0, 1.5).ry(1, 2.5).cx(0, 1)
        qasm = to_openqasm(original)
        restored = from_openqasm(qasm)

        assert restored.gates[0].params[0] == pytest.approx(1.5)
        assert restored.gates[1].params[0] == pytest.approx(2.5)

    def test_roundtrip_all_gates(self):
        """Complex circuit with many gates survives round-trip."""
        original = Circuit(3)
        original.h(0).x(1).y(2).z(0).s(1).t(2).i(0)
        original.rx(0, 0.5).ry(1, 1.0).rz(2, 1.5)
        original.cx(0, 1).cz(1, 2).swap(0, 2)
        original.ccx(0, 1, 2)

        qasm = to_openqasm(original)
        restored = from_openqasm(qasm)

        assert len(restored.gates) == len(original.gates)
        for orig, rest in zip(original.gates, restored.gates, strict=True):
            assert type(orig) is type(rest)
            assert orig.qubits == rest.qubits
            if orig.params:
                for p1, p2 in zip(orig.params, rest.params, strict=True):
                    assert p1 == pytest.approx(p2)


class TestSafeParamParsing:
    """Security tests: ensure QASM parameter parsing rejects code injection."""

    def test_simple_number(self):
        """Plain numbers should parse fine."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(1.5707963) q[0];'
        c = from_openqasm(qasm)
        assert c.gates[0].params[0] == pytest.approx(1.5707963)

    def test_pi_expression(self):
        """pi/2 should be handled safely."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(pi/2) q[0];'
        c = from_openqasm(qasm)
        assert c.gates[0].params[0] == pytest.approx(math.pi / 2)

    def test_negative_pi(self):
        """-pi should work."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(-pi) q[0];'
        c = from_openqasm(qasm)
        assert c.gates[0].params[0] == pytest.approx(-math.pi)

    def test_rejects_import(self):
        """__import__('os') must be rejected."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(__import__("os").system("echo pwned")) q[0];'
        with pytest.raises(ValueError):
            from_openqasm(qasm)

    def test_rejects_exec(self):
        """exec() must be rejected."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(exec("import os")) q[0];'
        with pytest.raises(ValueError):
            from_openqasm(qasm)

    def test_rejects_open(self):
        """open() must be rejected."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(open("/etc/passwd").read()) q[0];'
        with pytest.raises(ValueError):
            from_openqasm(qasm)

    def test_rejects_dunder_builtins(self):
        """__builtins__ access must be rejected."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(__builtins__) q[0];'
        with pytest.raises(ValueError, match="Unsafe parameter expression rejected"):
            from_openqasm(qasm)

    def test_rejects_arbitrary_string(self):
        """Arbitrary strings must be rejected."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(malicious_func()) q[0];'
        with pytest.raises(ValueError):
            from_openqasm(qasm)

    def test_arithmetic_expression(self):
        """Safe arithmetic like 2*3.14/4 should work."""
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\nrx(2*pi/4) q[0];'
        c = from_openqasm(qasm)
        assert c.gates[0].params[0] == pytest.approx(math.pi / 2)

    def test_safe_eval_rejects_names_directly(self):
        """Direct test of _safe_eval_param to ensure name-based attacks fail."""
        from quantsdk.interop.openqasm import _safe_eval_param

        # Valid expressions
        assert _safe_eval_param("3.14") == pytest.approx(3.14)
        assert _safe_eval_param("1 + 2") == pytest.approx(3.0)
        assert _safe_eval_param("2 * 3.0 / 4") == pytest.approx(1.5)
        assert _safe_eval_param("-1.5") == pytest.approx(-1.5)
        assert _safe_eval_param("(1 + 2) * 3") == pytest.approx(9.0)

        # Malicious expressions must be rejected by regex
        for malicious in [
            "__import__('os')",
            "open('/etc/passwd')",
            "exec('code')",
            "eval('1+1')",
            "os.system('ls')",
            "lambda: None",
            "a = 1",
        ]:
            with pytest.raises(ValueError, match="Unsafe parameter expression rejected"):
                _safe_eval_param(malicious)
