# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Local statevector simulator backend.

A pure-NumPy quantum simulator that executes circuits by building and
applying unitary matrices. Suitable for circuits up to ~20 qubits
on a standard machine.
"""

from __future__ import annotations

import uuid
from collections import Counter
from typing import Any

import numpy as np

from quantsdk.backend import Backend, BackendInfo, BackendStatus
from quantsdk.circuit import Circuit
from quantsdk.gates import Gate, Measure
from quantsdk.result import Result


class LocalSimulator(Backend):
    """A local statevector simulator for quantum circuits.

    Simulates quantum circuits by computing the full statevector and
    sampling measurement outcomes. No external dependencies beyond NumPy.

    Supports up to ~20 qubits on a typical machine (2^20 = 1M amplitudes).

    Example::

        from quantsdk.simulators.local import LocalSimulator

        sim = LocalSimulator()
        result = sim.run(circuit, shots=1000)
        print(result.counts)
    """

    MAX_QUBITS = 24  # Safety limit to prevent OOM

    def info(self) -> BackendInfo:
        return BackendInfo(
            name="local_simulator",
            provider="quantsdk",
            num_qubits=self.MAX_QUBITS,
            status=BackendStatus.ONLINE,
            is_simulator=True,
            native_gates=frozenset(
                ["H", "X", "Y", "Z", "S", "T", "I", "RX", "RY", "RZ", "U3",
                 "CX", "CZ", "SWAP", "RZZ", "CCX", "CSWAP"]
            ),
            max_shots=1_000_000,
            queue_depth=0,
        )

    def run(self, circuit: Circuit, shots: int = 1024, **options: Any) -> Result:
        """Execute a circuit on the local simulator.

        Args:
            circuit: The quantum circuit to simulate.
            shots: Number of measurement samples.
            **options:
                seed (int): Random seed for reproducibility.

        Returns:
            Result with measurement counts.

        Raises:
            ValueError: If circuit exceeds MAX_QUBITS.
        """
        n = circuit.num_qubits
        if n > self.MAX_QUBITS:
            raise ValueError(
                f"Circuit has {n} qubits, but local simulator supports at most {self.MAX_QUBITS}. "
                f"Use a GPU simulator or cloud backend for larger circuits."
            )

        seed = options.get("seed")
        rng = np.random.default_rng(seed)

        # Initialize |00...0⟩ state
        statevector = np.zeros(2**n, dtype=complex)
        statevector[0] = 1.0

        # Find which qubits are measured
        measured_qubits: list[int] = []

        # Apply gates
        for gate in circuit.gates:
            if isinstance(gate, Measure):
                measured_qubits.append(gate.qubits[0])
                continue
            if gate.name == "BARRIER":
                continue

            statevector = self._apply_gate(statevector, gate, n)

        # If no measurements, measure all qubits
        if not measured_qubits:
            measured_qubits = list(range(n))

        # Sample from probability distribution
        probabilities = np.abs(statevector) ** 2
        probabilities = probabilities / probabilities.sum()  # Normalize for numerical stability

        indices = rng.choice(2**n, size=shots, p=probabilities)

        # Convert indices to bitstrings (only measured qubits)
        outcomes: list[str] = []
        for idx in indices:
            full_bitstring = format(idx, f"0{n}b")
            measured_bits = "".join(full_bitstring[q] for q in measured_qubits)
            outcomes.append(measured_bits)

        counts = dict(Counter(outcomes))

        return Result(
            counts=counts,
            shots=shots,
            backend="local_simulator",
            job_id=f"local-{uuid.uuid4().hex[:12]}",
            metadata={
                "simulator": "quantsdk_local",
                "num_qubits": n,
                "circuit_depth": circuit.depth,
                "seed": seed,
            },
        )

    def _apply_gate(self, statevector: np.ndarray, gate: Gate, n: int) -> np.ndarray:
        """Apply a gate to the statevector.

        Constructs the full 2^n x 2^n unitary by tensoring the gate matrix
        with identity matrices, then applies it to the statevector.
        """
        gate_matrix = gate.matrix()
        qubits = gate.qubits

        if gate.num_qubits == 1:
            return self._apply_single_qubit_gate(statevector, gate_matrix, qubits[0], n)
        elif gate.num_qubits == 2:
            return self._apply_two_qubit_gate(statevector, gate_matrix, qubits[0], qubits[1], n)
        elif gate.num_qubits == 3:
            return self._apply_multi_qubit_gate(statevector, gate_matrix, list(qubits), n)
        else:
            raise ValueError(f"Gates acting on {gate.num_qubits} qubits not supported")

    def _apply_single_qubit_gate(
        self, sv: np.ndarray, matrix: np.ndarray, qubit: int, n: int
    ) -> np.ndarray:
        """Efficiently apply a single-qubit gate without building full unitary."""
        sv = sv.reshape([2] * n)
        # Apply the 2x2 matrix along the qubit axis
        sv = np.tensordot(matrix, sv, axes=([1], [qubit]))
        # Move the new axis back to the correct position
        sv = np.moveaxis(sv, 0, qubit)
        return sv.reshape(2**n)

    def _apply_two_qubit_gate(
        self, sv: np.ndarray, matrix: np.ndarray, q0: int, q1: int, n: int
    ) -> np.ndarray:
        """Efficiently apply a two-qubit gate."""
        sv = sv.reshape([2] * n)
        matrix_reshaped = matrix.reshape(2, 2, 2, 2)
        # Contract over qubits q0 and q1
        sv = np.tensordot(matrix_reshaped, sv, axes=([2, 3], [q0, q1]))
        # Move axes back: the result has the two new axes at positions 0, 1
        # We need to move them to q0 and q1
        sv = np.moveaxis(sv, [0, 1], sorted([q0, q1]))
        return sv.reshape(2**n)

    def _apply_multi_qubit_gate(
        self, sv: np.ndarray, matrix: np.ndarray, qubits: list[int], n: int
    ) -> np.ndarray:
        """Apply a multi-qubit gate (3+ qubits) using tensor contraction."""
        k = len(qubits)
        sv = sv.reshape([2] * n)
        matrix_reshaped = matrix.reshape([2] * (2 * k))
        # Contract over the qubit axes
        contraction_axes = list(range(k, 2 * k))
        sv = np.tensordot(matrix_reshaped, sv, axes=(contraction_axes, qubits))
        # Move axes back
        sv = np.moveaxis(sv, list(range(k)), sorted(qubits))
        return sv.reshape(2**n)
