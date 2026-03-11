# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Quantum gate definitions.

Provides the Gate base class and all standard gate implementations.
Each gate stores its name, target qubits, control qubits, and parameters.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


@dataclass(frozen=True, slots=True)
class Gate:
    """Base class for all quantum gates.

    Attributes:
        name: Human-readable gate name (e.g., "H", "CNOT", "RZ").
        qubits: Tuple of qubit indices this gate acts on.
        params: Tuple of float parameters (e.g., rotation angles).
        num_qubits: Number of qubits this gate acts on.
    """

    name: str
    qubits: tuple[int, ...]
    params: tuple[float, ...] = field(default_factory=tuple)

    @property
    def num_qubits(self) -> int:
        """Number of qubits this gate acts on."""
        return len(self.qubits)

    def matrix(self) -> np.ndarray:
        """Return the unitary matrix representation of this gate.

        Returns:
            A 2^n × 2^n complex numpy array representing the gate unitary.

        Raises:
            NotImplementedError: If matrix is not defined for this gate.
        """
        raise NotImplementedError(f"Matrix not implemented for gate '{self.name}'")

    def __repr__(self) -> str:
        params_str = f", params={self.params}" if self.params else ""
        return f"Gate({self.name}, qubits={self.qubits}{params_str})"


# ─── Single-Qubit Gates ───


class HGate(Gate):
    """Hadamard gate."""

    def __init__(self, qubit: int) -> None:
        object.__setattr__(self, "name", "H")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)


class XGate(Gate):
    """Pauli-X (NOT) gate."""

    def __init__(self, qubit: int) -> None:
        object.__setattr__(self, "name", "X")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array([[0, 1], [1, 0]], dtype=complex)


class YGate(Gate):
    """Pauli-Y gate."""

    def __init__(self, qubit: int) -> None:
        object.__setattr__(self, "name", "Y")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array([[0, -1j], [1j, 0]], dtype=complex)


class ZGate(Gate):
    """Pauli-Z gate."""

    def __init__(self, qubit: int) -> None:
        object.__setattr__(self, "name", "Z")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array([[1, 0], [0, -1]], dtype=complex)


class SGate(Gate):
    """S (√Z) gate — phase gate with π/2 rotation."""

    def __init__(self, qubit: int) -> None:
        object.__setattr__(self, "name", "S")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array([[1, 0], [0, 1j]], dtype=complex)


class TGate(Gate):
    """T (√S) gate — phase gate with π/4 rotation."""

    def __init__(self, qubit: int) -> None:
        object.__setattr__(self, "name", "T")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex)


class IGate(Gate):
    """Identity gate."""

    def __init__(self, qubit: int) -> None:
        object.__setattr__(self, "name", "I")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.eye(2, dtype=complex)


# ─── Parametric Single-Qubit Gates ───


class RXGate(Gate):
    """Rotation around X-axis by angle theta."""

    def __init__(self, qubit: int, theta: float) -> None:
        object.__setattr__(self, "name", "RX")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", (theta,))

    def matrix(self) -> np.ndarray:
        theta = self.params[0]
        cos = math.cos(theta / 2)
        sin = math.sin(theta / 2)
        return np.array([[cos, -1j * sin], [-1j * sin, cos]], dtype=complex)


class RYGate(Gate):
    """Rotation around Y-axis by angle theta."""

    def __init__(self, qubit: int, theta: float) -> None:
        object.__setattr__(self, "name", "RY")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", (theta,))

    def matrix(self) -> np.ndarray:
        theta = self.params[0]
        cos = math.cos(theta / 2)
        sin = math.sin(theta / 2)
        return np.array([[cos, -sin], [sin, cos]], dtype=complex)


class RZGate(Gate):
    """Rotation around Z-axis by angle theta."""

    def __init__(self, qubit: int, theta: float) -> None:
        object.__setattr__(self, "name", "RZ")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", (theta,))

    def matrix(self) -> np.ndarray:
        theta = self.params[0]
        return np.array(
            [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex
        )


class U3Gate(Gate):
    """General single-qubit rotation U3(theta, phi, lambda)."""

    def __init__(self, qubit: int, theta: float, phi: float, lam: float) -> None:
        object.__setattr__(self, "name", "U3")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", (theta, phi, lam))

    def matrix(self) -> np.ndarray:
        theta, phi, lam = self.params
        cos = math.cos(theta / 2)
        sin = math.sin(theta / 2)
        return np.array(
            [
                [cos, -np.exp(1j * lam) * sin],
                [np.exp(1j * phi) * sin, np.exp(1j * (phi + lam)) * cos],
            ],
            dtype=complex,
        )


# ─── Two-Qubit Gates ───


class CXGate(Gate):
    """Controlled-X (CNOT) gate."""

    def __init__(self, control: int, target: int) -> None:
        object.__setattr__(self, "name", "CX")
        object.__setattr__(self, "qubits", (control, target))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex
        )


class CZGate(Gate):
    """Controlled-Z gate."""

    def __init__(self, control: int, target: int) -> None:
        object.__setattr__(self, "name", "CZ")
        object.__setattr__(self, "qubits", (control, target))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dtype=complex
        )


class SwapGate(Gate):
    """SWAP gate — swaps two qubits."""

    def __init__(self, qubit1: int, qubit2: int) -> None:
        object.__setattr__(self, "name", "SWAP")
        object.__setattr__(self, "qubits", (qubit1, qubit2))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        return np.array(
            [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex
        )


class RZZGate(Gate):
    """ZZ-rotation gate RZZ(theta) = exp(-i * theta/2 * Z⊗Z)."""

    def __init__(self, qubit1: int, qubit2: int, theta: float) -> None:
        object.__setattr__(self, "name", "RZZ")
        object.__setattr__(self, "qubits", (qubit1, qubit2))
        object.__setattr__(self, "params", (theta,))

    def matrix(self) -> np.ndarray:
        theta = self.params[0]
        diag = np.exp(-1j * theta / 2)
        anti_diag = np.exp(1j * theta / 2)
        return np.diag([diag, anti_diag, anti_diag, diag]).astype(complex)


# ─── Three-Qubit Gates ───


class ToffoliGate(Gate):
    """Toffoli (CCX) gate — double-controlled NOT."""

    def __init__(self, control1: int, control2: int, target: int) -> None:
        object.__setattr__(self, "name", "CCX")
        object.__setattr__(self, "qubits", (control1, control2, target))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        m = np.eye(8, dtype=complex)
        m[6, 6] = 0
        m[7, 7] = 0
        m[6, 7] = 1
        m[7, 6] = 1
        return m


class FredkinGate(Gate):
    """Fredkin (CSWAP) gate — controlled SWAP."""

    def __init__(self, control: int, target1: int, target2: int) -> None:
        object.__setattr__(self, "name", "CSWAP")
        object.__setattr__(self, "qubits", (control, target1, target2))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        m = np.eye(8, dtype=complex)
        m[5, 5] = 0
        m[6, 6] = 0
        m[5, 6] = 1
        m[6, 5] = 1
        return m


# ─── Special Gates ───


class Measure(Gate):
    """Measurement in the computational basis."""

    def __init__(self, qubit: int, classical_bit: int | None = None) -> None:
        object.__setattr__(self, "name", "MEASURE")
        object.__setattr__(self, "qubits", (qubit,))
        object.__setattr__(self, "params", ())
        # Store classical bit mapping (not in params since it's not a float)
        object.__setattr__(self, "classical_bit", classical_bit)

    def matrix(self) -> np.ndarray:
        raise NotImplementedError("Measurement is not a unitary operation")


class Barrier(Gate):
    """Barrier — prevents gate optimization across this point."""

    def __init__(self, qubits: Sequence[int]) -> None:
        object.__setattr__(self, "name", "BARRIER")
        object.__setattr__(self, "qubits", tuple(qubits))
        object.__setattr__(self, "params", ())

    def matrix(self) -> np.ndarray:
        raise NotImplementedError("Barrier is not a unitary operation")


# ─── Gate Registry ───

GATE_MAP: dict[str, type[Gate]] = {
    "h": HGate,
    "x": XGate,
    "y": YGate,
    "z": ZGate,
    "s": SGate,
    "t": TGate,
    "i": IGate,
    "id": IGate,
    "rx": RXGate,
    "ry": RYGate,
    "rz": RZGate,
    "u3": U3Gate,
    "cx": CXGate,
    "cnot": CXGate,
    "cz": CZGate,
    "swap": SwapGate,
    "rzz": RZZGate,
    "ccx": ToffoliGate,
    "toffoli": ToffoliGate,
    "cswap": FredkinGate,
    "fredkin": FredkinGate,
}
