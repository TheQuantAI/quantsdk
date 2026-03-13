# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Quantum Circuit — the core abstraction of QuantSDK.

A Circuit represents a sequence of quantum gates applied to qubits.
It is framework-agnostic and can be exported to Qiskit, Cirq, PennyLane,
or OpenQASM for execution on any backend.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

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


class Circuit:
    """A framework-agnostic quantum circuit.

    Create quantum circuits using a clean, Pythonic API and run them on any
    backend — IBM Quantum, IonQ, simulators, and more.

    Args:
        num_qubits: Number of qubits in the circuit.
        name: Optional name for the circuit.

    Example::

        import quantsdk as qs

        circuit = qs.Circuit(2, name="bell_state")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()
    """

    def __init__(self, num_qubits: int, name: str = "circuit") -> None:
        if num_qubits <= 0:
            raise ValueError(f"num_qubits must be positive, got {num_qubits}")
        self._num_qubits = num_qubits
        self._name = name
        self._gates: list[Gate] = []

    # ─── Properties ───

    @property
    def num_qubits(self) -> int:
        """Number of qubits in the circuit."""
        return self._num_qubits

    @property
    def name(self) -> str:
        """Name of the circuit."""
        return self._name

    @property
    def gates(self) -> list[Gate]:
        """List of gates in the circuit (read-only copy)."""
        return list(self._gates)

    @property
    def depth(self) -> int:
        """Circuit depth — the number of time steps needed to execute all gates.

        Gates on different qubits can execute in parallel (same time step).
        """
        if not self._gates:
            return 0

        # Track the depth at each qubit
        qubit_depth: list[int] = [0] * self._num_qubits

        for gate in self._gates:
            if gate.name in ("MEASURE", "BARRIER"):
                continue
            # Gate starts at the max depth of all its qubits
            max_depth = max(qubit_depth[q] for q in gate.qubits)
            new_depth = max_depth + 1
            for q in gate.qubits:
                qubit_depth[q] = new_depth

        return max(qubit_depth) if qubit_depth else 0

    @property
    def gate_count(self) -> int:
        """Total number of gates (excluding measurements and barriers)."""
        return sum(1 for g in self._gates if g.name not in ("MEASURE", "BARRIER"))

    @property
    def num_measurements(self) -> int:
        """Number of measurement operations in the circuit."""
        return sum(1 for g in self._gates if g.name == "MEASURE")

    # ─── Qubit Validation ───

    def _validate_qubit(self, qubit: int) -> None:
        """Validate that a qubit index is within range."""
        if not 0 <= qubit < self._num_qubits:
            raise IndexError(
                f"Qubit index {qubit} out of range for circuit with {self._num_qubits} qubits"
            )

    def _validate_qubits(self, *qubits: int) -> None:
        """Validate multiple qubit indices."""
        for q in qubits:
            self._validate_qubit(q)
        if len(set(qubits)) != len(qubits):
            raise ValueError(f"Duplicate qubit indices: {qubits}")

    # ─── Single-Qubit Gates ───

    def h(self, qubit: int) -> Circuit:
        """Apply Hadamard gate."""
        self._validate_qubit(qubit)
        self._gates.append(HGate(qubit))
        return self

    def x(self, qubit: int) -> Circuit:
        """Apply Pauli-X (NOT) gate."""
        self._validate_qubit(qubit)
        self._gates.append(XGate(qubit))
        return self

    def y(self, qubit: int) -> Circuit:
        """Apply Pauli-Y gate."""
        self._validate_qubit(qubit)
        self._gates.append(YGate(qubit))
        return self

    def z(self, qubit: int) -> Circuit:
        """Apply Pauli-Z gate."""
        self._validate_qubit(qubit)
        self._gates.append(ZGate(qubit))
        return self

    def s(self, qubit: int) -> Circuit:
        """Apply S (√Z) gate."""
        self._validate_qubit(qubit)
        self._gates.append(SGate(qubit))
        return self

    def t(self, qubit: int) -> Circuit:
        """Apply T (√S) gate."""
        self._validate_qubit(qubit)
        self._gates.append(TGate(qubit))
        return self

    def i(self, qubit: int) -> Circuit:
        """Apply Identity gate."""
        self._validate_qubit(qubit)
        self._gates.append(IGate(qubit))
        return self

    def sdg(self, qubit: int) -> Circuit:
        """Apply S-dagger gate."""
        self._validate_qubit(qubit)
        self._gates.append(SdgGate(qubit))
        return self

    def tdg(self, qubit: int) -> Circuit:
        """Apply T-dagger gate."""
        self._validate_qubit(qubit)
        self._gates.append(TdgGate(qubit))
        return self

    def sx(self, qubit: int) -> Circuit:
        """Apply square root of X gate."""
        self._validate_qubit(qubit)
        self._gates.append(SXGate(qubit))
        return self

    def sxdg(self, qubit: int) -> Circuit:
        """Apply square root of X dagger gate."""
        self._validate_qubit(qubit)
        self._gates.append(SXdgGate(qubit))
        return self

    # ─── Parametric Single-Qubit Gates ───

    def rx(self, qubit: int, theta: float) -> Circuit:
        """Apply RX rotation gate (rotation around X-axis)."""
        self._validate_qubit(qubit)
        self._gates.append(RXGate(qubit, theta))
        return self

    def ry(self, qubit: int, theta: float) -> Circuit:
        """Apply RY rotation gate (rotation around Y-axis)."""
        self._validate_qubit(qubit)
        self._gates.append(RYGate(qubit, theta))
        return self

    def rz(self, qubit: int, theta: float) -> Circuit:
        """Apply RZ rotation gate (rotation around Z-axis)."""
        self._validate_qubit(qubit)
        self._gates.append(RZGate(qubit, theta))
        return self

    def u3(self, qubit: int, theta: float, phi: float, lam: float) -> Circuit:
        """Apply general single-qubit rotation U3(theta, phi, lambda)."""
        self._validate_qubit(qubit)
        self._gates.append(U3Gate(qubit, theta, phi, lam))
        return self

    def p(self, qubit: int, lam: float) -> Circuit:
        """Apply Phase gate P(lam)."""
        self._validate_qubit(qubit)
        self._gates.append(PhaseGate(qubit, lam))
        return self

    def u1(self, qubit: int, lam: float) -> Circuit:
        """Apply U1 gate (equivalent to Phase)."""
        self._validate_qubit(qubit)
        self._gates.append(U1Gate(qubit, lam))
        return self

    def u2(self, qubit: int, phi: float, lam: float) -> Circuit:
        """Apply U2 gate."""
        self._validate_qubit(qubit)
        self._gates.append(U2Gate(qubit, phi, lam))
        return self

    def r(self, qubit: int, theta: float, phi: float) -> Circuit:
        """Apply general rotation R(theta, phi) gate."""
        self._validate_qubit(qubit)
        self._gates.append(RGate(qubit, theta, phi))
        return self

    # ─── Two-Qubit Gates ───

    def cx(self, control: int, target: int) -> Circuit:
        """Apply Controlled-X (CNOT) gate."""
        self._validate_qubits(control, target)
        self._gates.append(CXGate(control, target))
        return self

    def cnot(self, control: int, target: int) -> Circuit:
        """Apply CNOT gate (alias for cx)."""
        return self.cx(control, target)

    def cz(self, control: int, target: int) -> Circuit:
        """Apply Controlled-Z gate."""
        self._validate_qubits(control, target)
        self._gates.append(CZGate(control, target))
        return self

    def swap(self, qubit1: int, qubit2: int) -> Circuit:
        """Apply SWAP gate."""
        self._validate_qubits(qubit1, qubit2)
        self._gates.append(SwapGate(qubit1, qubit2))
        return self

    def rzz(self, qubit1: int, qubit2: int, theta: float) -> Circuit:
        """Apply RZZ gate (ZZ-rotation)."""
        self._validate_qubits(qubit1, qubit2)
        self._gates.append(RZZGate(qubit1, qubit2, theta))
        return self

    # ─── Controlled Gates ───

    def cy(self, control: int, target: int) -> Circuit:
        """Apply Controlled-Y gate."""
        self._validate_qubits(control, target)
        self._gates.append(CYGate(control, target))
        return self

    def ch(self, control: int, target: int) -> Circuit:
        """Apply Controlled-Hadamard gate."""
        self._validate_qubits(control, target)
        self._gates.append(CHGate(control, target))
        return self

    def cs(self, control: int, target: int) -> Circuit:
        """Apply Controlled-S gate."""
        self._validate_qubits(control, target)
        self._gates.append(CSGate(control, target))
        return self

    def csdg(self, control: int, target: int) -> Circuit:
        """Apply Controlled-S-dagger gate."""
        self._validate_qubits(control, target)
        self._gates.append(CSdgGate(control, target))
        return self

    def crx(self, control: int, target: int, theta: float) -> Circuit:
        """Apply Controlled-RX gate."""
        self._validate_qubits(control, target)
        self._gates.append(CRXGate(control, target, theta))
        return self

    def cry(self, control: int, target: int, theta: float) -> Circuit:
        """Apply Controlled-RY gate."""
        self._validate_qubits(control, target)
        self._gates.append(CRYGate(control, target, theta))
        return self

    def crz(self, control: int, target: int, theta: float) -> Circuit:
        """Apply Controlled-RZ gate."""
        self._validate_qubits(control, target)
        self._gates.append(CRZGate(control, target, theta))
        return self

    def cp(self, control: int, target: int, lam: float) -> Circuit:
        """Apply Controlled-Phase gate."""
        self._validate_qubits(control, target)
        self._gates.append(CPhaseGate(control, target, lam))
        return self

    def cu1(self, control: int, target: int, lam: float) -> Circuit:
        """Apply Controlled-U1 gate."""
        self._validate_qubits(control, target)
        self._gates.append(CU1Gate(control, target, lam))
        return self

    def cu3(self, control: int, target: int, theta: float, phi: float, lam: float) -> Circuit:
        """Apply Controlled-U3 gate."""
        self._validate_qubits(control, target)
        self._gates.append(CU3Gate(control, target, theta, phi, lam))
        return self

    def csx(self, control: int, target: int) -> Circuit:
        """Apply Controlled-SX gate."""
        self._validate_qubits(control, target)
        self._gates.append(CSXGate(control, target))
        return self

    # ─── Two-Qubit Rotation Gates ───

    def rxx(self, qubit1: int, qubit2: int, theta: float) -> Circuit:
        """Apply RXX gate (XX-rotation)."""
        self._validate_qubits(qubit1, qubit2)
        self._gates.append(RXXGate(qubit1, qubit2, theta))
        return self

    def ryy(self, qubit1: int, qubit2: int, theta: float) -> Circuit:
        """Apply RYY gate (YY-rotation)."""
        self._validate_qubits(qubit1, qubit2)
        self._gates.append(RYYGate(qubit1, qubit2, theta))
        return self

    def rzx(self, qubit1: int, qubit2: int, theta: float) -> Circuit:
        """Apply RZX gate (ZX-rotation)."""
        self._validate_qubits(qubit1, qubit2)
        self._gates.append(RZXGate(qubit1, qubit2, theta))
        return self

    # ─── Two-Qubit Special Gates ───

    def iswap(self, qubit1: int, qubit2: int) -> Circuit:
        """Apply iSWAP gate."""
        self._validate_qubits(qubit1, qubit2)
        self._gates.append(iSwapGate(qubit1, qubit2))
        return self

    def dcx(self, qubit1: int, qubit2: int) -> Circuit:
        """Apply Double-CX gate."""
        self._validate_qubits(qubit1, qubit2)
        self._gates.append(DCXGate(qubit1, qubit2))
        return self

    def ecr(self, qubit1: int, qubit2: int) -> Circuit:
        """Apply Echoed Cross-Resonance gate."""
        self._validate_qubits(qubit1, qubit2)
        self._gates.append(ECRGate(qubit1, qubit2))
        return self

    # ─── Three-Qubit Gates ───

    def ccx(self, control1: int, control2: int, target: int) -> Circuit:
        """Apply Toffoli (CCX) gate."""
        self._validate_qubits(control1, control2, target)
        self._gates.append(ToffoliGate(control1, control2, target))
        return self

    def toffoli(self, control1: int, control2: int, target: int) -> Circuit:
        """Apply Toffoli gate (alias for ccx)."""
        return self.ccx(control1, control2, target)

    def cswap(self, control: int, target1: int, target2: int) -> Circuit:
        """Apply Fredkin (CSWAP) gate."""
        self._validate_qubits(control, target1, target2)
        self._gates.append(FredkinGate(control, target1, target2))
        return self

    def fredkin(self, control: int, target1: int, target2: int) -> Circuit:
        """Apply Fredkin gate (alias for cswap)."""
        return self.cswap(control, target1, target2)

    def ccz(self, control1: int, control2: int, target: int) -> Circuit:
        """Apply CCZ (double-controlled Z) gate."""
        self._validate_qubits(control1, control2, target)
        self._gates.append(CCZGate(control1, control2, target))
        return self

    # ─── Measurement ───

    def measure(self, qubit: int, classical_bit: int | None = None) -> Circuit:
        """Measure a qubit in the computational basis.

        Args:
            qubit: Qubit index to measure.
            classical_bit: Optional classical bit to store the result.
                           Defaults to same index as qubit.
        """
        self._validate_qubit(qubit)
        self._gates.append(Measure(qubit, classical_bit))
        return self

    def measure_all(self) -> Circuit:
        """Measure all qubits in the computational basis."""
        for q in range(self._num_qubits):
            self._gates.append(Measure(q, q))
        return self

    # ─── Utility ───

    def barrier(self, qubits: Sequence[int] | None = None) -> Circuit:
        """Add a barrier to prevent gate optimization across this point."""
        if qubits is None:
            qubits = list(range(self._num_qubits))
        for q in qubits:
            self._validate_qubit(q)
        self._gates.append(Barrier(qubits))
        return self

    def reset(self, qubit: int) -> Circuit:
        """Reset a qubit to the |0> state."""
        self._validate_qubit(qubit)
        self._gates.append(Reset(qubit))
        return self

    def copy(self) -> Circuit:
        """Create a deep copy of this circuit."""
        new_circuit = Circuit(self._num_qubits, name=self._name)
        new_circuit._gates = list(self._gates)  # Gates are frozen dataclasses
        return new_circuit

    # ─── Framework Interop (convenience methods) ───

    def to_qiskit(self) -> Any:
        """Convert this circuit to a Qiskit QuantumCircuit.

        Requires: ``pip install quantsdk[ibm]``

        Returns:
            A ``qiskit.circuit.QuantumCircuit`` equivalent.

        Example::

            circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
            qiskit_circuit = circuit.to_qiskit()
        """
        from quantsdk.interop.qiskit_interop import to_qiskit

        return to_qiskit(self)

    def to_openqasm(self) -> str:
        """Export this circuit as an OpenQASM 2.0 string.

        Returns:
            An OpenQASM 2.0 compliant string.

        Example::

            circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
            print(circuit.to_openqasm())
        """
        from quantsdk.interop.openqasm import to_openqasm

        return to_openqasm(self)

    @classmethod
    def from_qiskit(cls, qiskit_circuit: Any) -> Circuit:
        """Create a QuantSDK Circuit from a Qiskit QuantumCircuit.

        Requires: ``pip install quantsdk[ibm]``

        Args:
            qiskit_circuit: A ``qiskit.circuit.QuantumCircuit``.

        Returns:
            A QuantSDK Circuit equivalent.
        """
        from quantsdk.interop.qiskit_interop import from_qiskit

        return from_qiskit(qiskit_circuit)

    @classmethod
    def from_openqasm(cls, qasm_str: str) -> Circuit:
        """Create a QuantSDK Circuit from an OpenQASM 2.0 string.

        Args:
            qasm_str: An OpenQASM 2.0 compliant string.

        Returns:
            A QuantSDK Circuit.
        """
        from quantsdk.interop.openqasm import from_openqasm

        return from_openqasm(qasm_str)

    # ─── Circuit Analysis ───

    def count_ops(self) -> dict[str, int]:
        """Count the number of each gate type in the circuit.

        Returns:
            Dictionary mapping gate name to count.
        """
        counts: dict[str, int] = {}
        for gate in self._gates:
            counts[gate.name] = counts.get(gate.name, 0) + 1
        return counts

    # ─── Text Drawing ───

    def draw(self) -> str:
        """Draw the circuit as ASCII art.

        Returns:
            String representation of the circuit.

        Example::

            >>> circuit = qs.Circuit(2)
            >>> circuit.h(0).cx(0, 1).measure_all()
            >>> print(circuit.draw())
            q0: ──H──●──M──
            q1: ─────X──M──
        """
        if not self._gates:
            return "\n".join(f"q{i}: ──" for i in range(self._num_qubits))

        # Each qubit gets a line. Build columns of gate symbols.
        lines: list[list[str]] = [[] for _ in range(self._num_qubits)]

        for gate in self._gates:
            if gate.name == "BARRIER":
                for q in range(self._num_qubits):
                    lines[q].append("|")
                continue

            if gate.name == "MEASURE":
                qubit = gate.qubits[0]
                for q in range(self._num_qubits):
                    lines[q].append("M" if q == qubit else "─")
                continue

            if gate.num_qubits == 1:
                qubit = gate.qubits[0]
                label = gate.name
                if gate.params:
                    param_str = ",".join(f"{p:.2f}" for p in gate.params)
                    label = f"{gate.name}({param_str})"
                for q in range(self._num_qubits):
                    lines[q].append(label if q == qubit else "─" * len(label))

            elif gate.num_qubits == 2:
                q0, q1 = gate.qubits
                min_q, max_q = min(q0, q1), max(q0, q1)

                # Determine symbols for control and target qubit
                _CONTROLLED_GATES = {
                    "CX": ("●", "X"), "CY": ("●", "Y"), "CZ": ("●", "●"),
                    "CH": ("●", "H"), "CS": ("●", "S"), "CSdg": ("●", "S†"),
                    "CSX": ("●", "SX"), "CRX": ("●", "RX"), "CRY": ("●", "RY"),
                    "CRZ": ("●", "RZ"), "CP": ("●", "P"), "CU1": ("●", "U1"),
                    "CU3": ("●", "U3"),
                }
                _SYMMETRIC_GATES = {
                    "SWAP": "x", "iSWAP": "iS", "RXX": "RXX", "RYY": "RYY",
                    "RZZ": "RZZ", "RZX": "RZX", "DCX": "DCX", "ECR": "ECR",
                }

                if gate.name in _CONTROLLED_GATES:
                    ctrl_sym, tgt_sym = _CONTROLLED_GATES[gate.name]
                    width = max(len(ctrl_sym), len(tgt_sym))
                    for q in range(self._num_qubits):
                        if q == q0:
                            lines[q].append(ctrl_sym.center(width))
                        elif q == q1:
                            lines[q].append(tgt_sym.center(width))
                        elif min_q < q < max_q:
                            lines[q].append("|".center(width))
                        else:
                            lines[q].append("─" * width)
                elif gate.name in _SYMMETRIC_GATES:
                    sym = _SYMMETRIC_GATES[gate.name]
                    for q in range(self._num_qubits):
                        if q in gate.qubits:
                            lines[q].append(sym)
                        elif min_q < q < max_q:
                            lines[q].append("|".center(len(sym)))
                        else:
                            lines[q].append("─" * len(sym))
                else:
                    # Fallback for unknown 2-qubit gates
                    label = gate.name
                    for q in range(self._num_qubits):
                        if q == q0:
                            lines[q].append(f"{label}₀")
                        elif q == q1:
                            lines[q].append(f"{label}₁")
                        elif min_q < q < max_q:
                            lines[q].append("|".center(len(label) + 1))
                        else:
                            lines[q].append("─" * (len(label) + 1))

            elif gate.num_qubits == 3:
                q0, q1, q2 = gate.qubits
                min_q = min(q0, q1, q2)
                max_q = max(q0, q1, q2)
                for q in range(self._num_qubits):
                    if gate.name == "CCX":
                        if q in (q0, q1):
                            lines[q].append("●")
                        elif q == q2:
                            lines[q].append("X")
                        elif min_q < q < max_q:
                            lines[q].append("|")
                        else:
                            lines[q].append("─")
                    else:
                        lines[q].append("─")

        # Format the output
        result_lines = []
        for q in range(self._num_qubits):
            prefix = f"q{q}: ──"
            body = "──".join(lines[q])
            result_lines.append(f"{prefix}{body}──")

        return "\n".join(result_lines)

    # ─── Dunder Methods ───

    def __len__(self) -> int:
        """Number of gates (including measurements)."""
        return len(self._gates)

    def __repr__(self) -> str:
        return (
            f"Circuit(num_qubits={self._num_qubits}, name='{self._name}', gates={len(self._gates)})"
        )

    def __str__(self) -> str:
        return self.draw()
