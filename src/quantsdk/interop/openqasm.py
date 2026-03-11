# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
OpenQASM 2.0 interop — export and import QuantSDK circuits as QASM strings.

Supports OpenQASM 2.0 (the most widely supported interchange format).
"""

from __future__ import annotations

import math
import re

from quantsdk.circuit import Circuit
from quantsdk.gates import (
    Barrier,
    CXGate,
    CZGate,
    FredkinGate,
    Gate,
    HGate,
    IGate,
    Measure,
    RXGate,
    RYGate,
    RZGate,
    RZZGate,
    SGate,
    SwapGate,
    TGate,
    ToffoliGate,
    U3Gate,
    XGate,
    YGate,
    ZGate,
)


def to_openqasm(circuit: Circuit) -> str:
    """Export a QuantSDK Circuit as an OpenQASM 2.0 string.

    Args:
        circuit: The QuantSDK circuit to convert.

    Returns:
        An OpenQASM 2.0 compliant string.

    Example::

        import quantsdk as qs
        from quantsdk.interop import to_openqasm

        circuit = qs.Circuit(2)
        circuit.h(0).cx(0, 1).measure_all()

        qasm_str = to_openqasm(circuit)
        print(qasm_str)
    """
    lines: list[str] = []

    # Header
    lines.append("OPENQASM 2.0;")
    lines.append('include "qelib1.inc";')
    lines.append("")

    # Register declarations
    lines.append(f"qreg q[{circuit.num_qubits}];")
    num_meas = circuit.num_measurements
    if num_meas > 0:
        lines.append(f"creg c[{num_meas}];")
    lines.append("")

    clbit_index = 0

    for gate in circuit.gates:
        line = _gate_to_qasm(gate, clbit_index)
        if line is not None:
            lines.append(line)
        if isinstance(gate, Measure):
            clbit_index += 1

    # Trailing newline
    lines.append("")
    return "\n".join(lines)


def _gate_to_qasm(gate: Gate, clbit_index: int) -> str | None:
    """Convert a single gate to its OpenQASM 2.0 representation."""
    q = gate.qubits

    if isinstance(gate, Measure):
        return f"measure q[{q[0]}] -> c[{clbit_index}];"

    if isinstance(gate, Barrier):
        qargs = ",".join(f"q[{i}]" for i in q)
        return f"barrier {qargs};"

    if isinstance(gate, HGate):
        return f"h q[{q[0]}];"

    if isinstance(gate, XGate):
        return f"x q[{q[0]}];"

    if isinstance(gate, YGate):
        return f"y q[{q[0]}];"

    if isinstance(gate, ZGate):
        return f"z q[{q[0]}];"

    if isinstance(gate, SGate):
        return f"s q[{q[0]}];"

    if isinstance(gate, TGate):
        return f"t q[{q[0]}];"

    if isinstance(gate, IGate):
        return f"id q[{q[0]}];"

    if isinstance(gate, RXGate):
        return f"rx({gate.params[0]}) q[{q[0]}];"

    if isinstance(gate, RYGate):
        return f"ry({gate.params[0]}) q[{q[0]}];"

    if isinstance(gate, RZGate):
        return f"rz({gate.params[0]}) q[{q[0]}];"

    if isinstance(gate, U3Gate):
        return f"u3({gate.params[0]},{gate.params[1]},{gate.params[2]}) q[{q[0]}];"

    if isinstance(gate, CXGate):
        return f"cx q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CZGate):
        return f"cz q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, SwapGate):
        return f"swap q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, RZZGate):
        return f"rzz({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, ToffoliGate):
        return f"ccx q[{q[0]}],q[{q[1]}],q[{q[2]}];"

    if isinstance(gate, FredkinGate):
        return f"cswap q[{q[0]}],q[{q[1]}],q[{q[2]}];"

    raise ValueError(f"Unsupported gate for OpenQASM export: {gate.name}")


# ─── OpenQASM 2.0 Parser ───

# Regex patterns for parsing
_RE_QREG = re.compile(r"qreg\s+(\w+)\[(\d+)\];")
_RE_CREG = re.compile(r"creg\s+(\w+)\[(\d+)\];")
_RE_MEASURE = re.compile(r"measure\s+(\w+)\[(\d+)\]\s*->\s*(\w+)\[(\d+)\];")
_RE_BARRIER = re.compile(r"barrier\s+(.+);")
_RE_GATE_NO_PARAM = re.compile(r"(\w+)\s+(.+);")
_RE_GATE_WITH_PARAM = re.compile(r"(\w+)\(([^)]+)\)\s+(.+);")
_RE_QUBIT = re.compile(r"(\w+)\[(\d+)\]")

# Mapping from QASM gate names to builder functions
_QASM_GATE_BUILDERS: dict[str, type[Gate]] = {
    "h": HGate,
    "x": XGate,
    "y": YGate,
    "z": ZGate,
    "s": SGate,
    "t": TGate,
    "id": IGate,
    "rx": RXGate,
    "ry": RYGate,
    "rz": RZGate,
    "u3": U3Gate,
    "u": U3Gate,  # Qiskit uses 'u' for u3
    "cx": CXGate,
    "cz": CZGate,
    "swap": SwapGate,
    "rzz": RZZGate,
    "ccx": ToffoliGate,
    "cswap": FredkinGate,
}


def _parse_qubits(qargs_str: str) -> list[int]:
    """Parse qubit arguments like 'q[0],q[1]' into a list of indices."""
    matches = _RE_QUBIT.findall(qargs_str)
    return [int(idx) for _, idx in matches]


def _parse_params(param_str: str) -> list[float]:
    """Parse parameter string like '3.14,1.57,0.0' into a list of floats.

    Supports pi expressions like 'pi/2', '2*pi', etc.
    """
    params = []
    for p in param_str.split(","):
        p = p.strip()
        # Replace 'pi' with math.pi for evaluation
        p = p.replace("pi", str(math.pi))
        try:
            params.append(float(eval(p)))
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Cannot parse parameter: '{p}'") from e
    return params


def from_openqasm(qasm_str: str) -> Circuit:
    """Parse an OpenQASM 2.0 string into a QuantSDK Circuit.

    Args:
        qasm_str: An OpenQASM 2.0 compliant string.

    Returns:
        A QuantSDK Circuit.

    Raises:
        ValueError: If the QASM string is malformed or contains unsupported gates.

    Example::

        from quantsdk.interop import from_openqasm

        qasm = '''
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        creg c[2];
        h q[0];
        cx q[0],q[1];
        measure q[0] -> c[0];
        measure q[1] -> c[1];
        '''

        circuit = from_openqasm(qasm)
        print(circuit.draw())
    """
    num_qubits = 0
    circuit: Circuit | None = None

    for raw_line in qasm_str.strip().splitlines():
        line = raw_line.strip()

        # Skip empty lines, comments, headers
        if not line or line.startswith("//"):
            continue
        if line.startswith("OPENQASM") or line.startswith("include"):
            continue

        # Parse qreg
        m = _RE_QREG.match(line)
        if m:
            num_qubits = int(m.group(2))
            circuit = Circuit(num_qubits)
            continue

        # Parse creg (we note it but don't need to act on it)
        m = _RE_CREG.match(line)
        if m:
            continue

        if circuit is None:
            raise ValueError("No qreg declaration found before gate instructions")

        # Parse measure
        m = _RE_MEASURE.match(line)
        if m:
            qubit = int(m.group(2))
            circuit.measure(qubit)
            continue

        # Parse barrier
        m = _RE_BARRIER.match(line)
        if m:
            qubits = _parse_qubits(m.group(1))
            circuit.barrier(qubits)
            continue

        # Parse gate with parameters: gate(params) qargs;
        m = _RE_GATE_WITH_PARAM.match(line)
        if m:
            gate_name = m.group(1).lower()
            params = _parse_params(m.group(2))
            qubits = _parse_qubits(m.group(3))
            _add_gate(circuit, gate_name, qubits, params)
            continue

        # Parse gate without parameters: gate qargs;
        m = _RE_GATE_NO_PARAM.match(line)
        if m:
            gate_name = m.group(1).lower()
            qubits = _parse_qubits(m.group(2))
            _add_gate(circuit, gate_name, qubits, [])
            continue

        raise ValueError(f"Cannot parse QASM line: '{line}'")

    if circuit is None:
        raise ValueError("No qreg declaration found in QASM string")

    return circuit


def _add_gate(
    circuit: Circuit,
    gate_name: str,
    qubits: list[int],
    params: list[float],
) -> None:
    """Add a parsed gate to the circuit."""
    gate_class = _QASM_GATE_BUILDERS.get(gate_name)
    if gate_class is None:
        raise ValueError(
            f"Unsupported QASM gate: '{gate_name}'. "
            f"Supported: {sorted(_QASM_GATE_BUILDERS.keys())}"
        )

    # Build the gate based on its class
    if gate_class in (HGate, XGate, YGate, ZGate, SGate, TGate, IGate):
        circuit._gates.append(gate_class(qubits[0]))

    elif gate_class in (RXGate, RYGate, RZGate):
        circuit._gates.append(gate_class(qubits[0], params[0]))

    elif gate_class is U3Gate:
        circuit._gates.append(U3Gate(qubits[0], params[0], params[1], params[2]))

    elif gate_class in (CXGate, CZGate, SwapGate):
        circuit._gates.append(gate_class(qubits[0], qubits[1]))

    elif gate_class is RZZGate:
        circuit._gates.append(RZZGate(qubits[0], qubits[1], params[0]))

    elif gate_class is ToffoliGate:
        circuit._gates.append(ToffoliGate(qubits[0], qubits[1], qubits[2]))

    elif gate_class is FredkinGate:
        circuit._gates.append(FredkinGate(qubits[0], qubits[1], qubits[2]))

    else:
        raise ValueError(f"Gate builder not implemented: {gate_name}")
