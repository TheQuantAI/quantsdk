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
    CXGate,
    CYGate,
    CZGate,
    DCXGate,
    ECRGate,
    FredkinGate,
    Gate,
    HGate,
    IGate,
    Measure,
    PhaseGate,
    Reset,
    RGate,
    RXGate,
    RXXGate,
    RYGate,
    RYYGate,
    RZGate,
    RZXGate,
    RZZGate,
    SdgGate,
    SGate,
    SwapGate,
    SXdgGate,
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

    if isinstance(gate, SdgGate):
        return f"sdg q[{q[0]}];"

    if isinstance(gate, TdgGate):
        return f"tdg q[{q[0]}];"

    if isinstance(gate, SXGate):
        return f"sx q[{q[0]}];"

    if isinstance(gate, SXdgGate):
        return f"sxdg q[{q[0]}];"

    if isinstance(gate, PhaseGate):
        return f"p({gate.params[0]}) q[{q[0]}];"

    if isinstance(gate, U1Gate):
        return f"u1({gate.params[0]}) q[{q[0]}];"

    if isinstance(gate, U2Gate):
        return f"u2({gate.params[0]},{gate.params[1]}) q[{q[0]}];"

    if isinstance(gate, RGate):
        return f"r({gate.params[0]},{gate.params[1]}) q[{q[0]}];"

    if isinstance(gate, CYGate):
        return f"cy q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CHGate):
        return f"ch q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CSGate):
        return f"cs q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CSdgGate):
        return f"csdg q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CRXGate):
        return f"crx({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CRYGate):
        return f"cry({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CRZGate):
        return f"crz({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CPhaseGate):
        return f"cp({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CU1Gate):
        return f"cu1({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CU3Gate):
        return f"cu3({gate.params[0]},{gate.params[1]},{gate.params[2]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CSXGate):
        return f"csx q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, RXXGate):
        return f"rxx({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, RYYGate):
        return f"ryy({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, RZXGate):
        return f"rzx({gate.params[0]}) q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, iSwapGate):
        return f"iswap q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, DCXGate):
        return f"dcx q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, ECRGate):
        return f"ecr q[{q[0]}],q[{q[1]}];"

    if isinstance(gate, CCZGate):
        return f"ccz q[{q[0]}],q[{q[1]}],q[{q[2]}];"

    if isinstance(gate, Reset):
        return f"reset q[{q[0]}];"

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
    "sdg": SdgGate,
    "t": TGate,
    "tdg": TdgGate,
    "sx": SXGate,
    "sxdg": SXdgGate,
    "id": IGate,
    "rx": RXGate,
    "ry": RYGate,
    "rz": RZGate,
    "p": PhaseGate,
    "u1": U1Gate,
    "u2": U2Gate,
    "r": RGate,
    "u3": U3Gate,
    "u": U3Gate,
    "cx": CXGate,
    "cz": CZGate,
    "cy": CYGate,
    "ch": CHGate,
    "cs": CSGate,
    "csdg": CSdgGate,
    "crx": CRXGate,
    "cry": CRYGate,
    "crz": CRZGate,
    "cp": CPhaseGate,
    "cu1": CU1Gate,
    "cu3": CU3Gate,
    "cu": CU3Gate,
    "csx": CSXGate,
    "swap": SwapGate,
    "iswap": iSwapGate,
    "dcx": DCXGate,
    "ecr": ECRGate,
    "rxx": RXXGate,
    "ryy": RYYGate,
    "rzz": RZZGate,
    "rzx": RZXGate,
    "ccx": ToffoliGate,
    "ccz": CCZGate,
    "cswap": FredkinGate,
}


def _parse_qubits(qargs_str: str) -> list[int]:
    """Parse qubit arguments like 'q[0],q[1]' into a list of indices."""
    matches = _RE_QUBIT.findall(qargs_str)
    return [int(idx) for _, idx in matches]


# ── Safe arithmetic evaluator (replaces eval) ──────────────────────────────
_SAFE_PARAM_RE = re.compile(
    r"^[\d\.eE+\-*/() ]+$"  # digits, decimal, scientific notation, operators, parens, spaces
)


def _safe_eval_param(expr: str) -> float:
    """Safely evaluate a simple arithmetic expression (no builtins, no names).

    Only allows: numbers, +, -, *, /, parentheses, and whitespace.
    The string 'pi' must already be substituted before calling this.

    Raises:
        ValueError: If the expression contains disallowed characters.
    """
    if not _SAFE_PARAM_RE.match(expr):
        raise ValueError(
            f"Unsafe parameter expression rejected: '{expr}'. "
            "Only numeric literals and +, -, *, / operators are allowed."
        )
    # ast.literal_eval doesn't handle arithmetic, so we use a restricted
    # compile + eval with empty globals/locals to prevent code injection.
    try:
        code = compile(expr, "<qasm_param>", "eval")
        # Verify the bytecode only contains safe operations
        for name in code.co_names:
            raise ValueError(f"Name '{name}' not allowed in parameter expression")
        # Sandboxed eval: regex-validated input, no builtins, no names allowed
        return float(eval(code, {"__builtins__": {}}, {}))  # noqa: S307 # nosec B307
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as e:
        raise ValueError(f"Cannot parse parameter: '{expr}'") from e


def _parse_params(param_str: str) -> list[float]:
    """Parse parameter string like '3.14,1.57,0.0' into a list of floats.

    Supports pi expressions like 'pi/2', '2*pi', etc.
    Uses a safe evaluator — no arbitrary code execution.
    """
    params = []
    for p in param_str.split(","):
        p = p.strip()
        # Replace 'pi' with its numeric value before safe evaluation
        p = p.replace("pi", str(math.pi))
        params.append(_safe_eval_param(p))
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

        # Parse reset
        m_reset = re.match(r"reset\s+(\w+)\[(\d+)\];", line)
        if m_reset:
            qubit = int(m_reset.group(2))
            circuit._gates.append(Reset(qubit))
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
    if gate_class in (
        HGate, XGate, YGate, ZGate, SGate, SdgGate,
        TGate, TdgGate, SXGate, SXdgGate, IGate,
    ):
        circuit._gates.append(gate_class(qubits[0]))

    elif gate_class in (RXGate, RYGate, RZGate, PhaseGate, U1Gate):
        circuit._gates.append(gate_class(qubits[0], params[0]))

    elif gate_class in (U2Gate, RGate):
        circuit._gates.append(gate_class(qubits[0], params[0], params[1]))

    elif gate_class is U3Gate:
        circuit._gates.append(U3Gate(qubits[0], params[0], params[1], params[2]))

    elif gate_class in (
        CXGate, CZGate, CYGate, CHGate, CSGate, CSdgGate,
        CSXGate, SwapGate, iSwapGate, DCXGate, ECRGate,
    ):
        circuit._gates.append(gate_class(qubits[0], qubits[1]))

    elif gate_class in (CRXGate, CRYGate, CRZGate, CPhaseGate, CU1Gate) or gate_class in (RXXGate, RYYGate, RZZGate, RZXGate):
        circuit._gates.append(gate_class(qubits[0], qubits[1], params[0]))

    elif gate_class is CU3Gate:
        circuit._gates.append(CU3Gate(qubits[0], qubits[1], params[0], params[1], params[2]))

    elif gate_class is ToffoliGate:
        circuit._gates.append(ToffoliGate(qubits[0], qubits[1], qubits[2]))

    elif gate_class is CCZGate:
        circuit._gates.append(CCZGate(qubits[0], qubits[1], qubits[2]))

    elif gate_class is FredkinGate:
        circuit._gates.append(FredkinGate(qubits[0], qubits[1], qubits[2]))

    else:
        raise ValueError(f"Gate builder not implemented: {gate_name}")
