# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
QuantRouter v0.1 — Rule-based quantum backend routing.

Analyzes a circuit's characteristics and selects the optimal backend
based on qubit count, gate composition, connectivity requirements,
and user constraints (cost, quality, speed).

This is the rule-based version (v0.1). ML-powered routing (v0.5) will
be added in Sprint 4 (Month 10) using GNN-based circuit embeddings.

Example::

    from quantsdk.router import QuantRouter, RoutingConstraints

    router = QuantRouter()
    decision = router.route(circuit, constraints=RoutingConstraints(
        optimize_for="quality",
        max_cost_usd=0.50,
    ))
    print(decision.backend)       # "ibm_brisbane"
    print(decision.reason)        # "Best fidelity match for 5-qubit circuit"
    print(decision.scores)        # {"ibm_brisbane": 0.87, "simulator_cpu": 0.65}
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ─── Enums ───


class OptimizeFor(Enum):
    """Optimization target for routing decisions."""

    QUALITY = "quality"
    SPEED = "speed"
    COST = "cost"


class AlgorithmClass(Enum):
    """Detected algorithm class of a circuit."""

    UNKNOWN = "unknown"
    BELL_STATE = "bell_state"
    GHZ = "ghz"
    QFT = "qft"
    VQE = "vqe"
    QAOA = "qaoa"
    GROVER = "grover"
    OPTIMIZATION = "optimization"
    VARIATIONAL = "variational"
    GENERAL = "general"


# ─── Data Classes ───


@dataclass(frozen=True)
class CircuitFeatures:
    """Extracted features of a quantum circuit for routing decisions.

    These features are also logged for QuantRouter ML training data
    collection (starting Month 6).

    Attributes:
        qubit_count: Number of qubits in the circuit.
        gate_count: Total number of gates.
        depth: Circuit depth (longest path from input to output).
        cx_count: Number of two-qubit (entangling) gates.
        gate_types: Set of gate type names used.
        single_qubit_gates: Count of single-qubit gates.
        two_qubit_gates: Count of two-qubit gates.
        three_qubit_gates: Count of three-qubit gates.
        measurement_count: Number of measurement operations.
        has_parameterized_gates: Whether circuit has rotation gates.
        algorithm_class: Detected algorithm class.
        connectivity: Set of qubit pairs that interact via 2-qubit gates.
    """

    qubit_count: int
    gate_count: int
    depth: int
    cx_count: int
    gate_types: frozenset[str]
    single_qubit_gates: int
    two_qubit_gates: int
    three_qubit_gates: int
    measurement_count: int
    has_parameterized_gates: bool
    algorithm_class: AlgorithmClass
    connectivity: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class BackendCapability:
    """Describes a backend's capabilities for routing scoring.

    Attributes:
        name: Backend identifier (e.g., "ibm_brisbane", "local_simulator").
        provider: Provider name ("ibm", "ionq", "simulator").
        num_qubits: Available qubit count.
        is_simulator: Whether this is a simulator.
        native_gates: Set of natively supported gate names.
        avg_single_qubit_fidelity: Average single-qubit gate fidelity (0-1).
        avg_two_qubit_fidelity: Average two-qubit gate fidelity (0-1).
        queue_depth: Current jobs in queue.
        avg_queue_time_sec: Average wait time in seconds.
        cost_per_shot: Cost per shot in USD.
        max_shots: Maximum shots per job.
        is_available: Whether the backend is currently online.
    """

    name: str
    provider: str
    num_qubits: int
    is_simulator: bool = False
    native_gates: frozenset[str] = field(default_factory=frozenset)
    avg_single_qubit_fidelity: float = 1.0
    avg_two_qubit_fidelity: float = 1.0
    queue_depth: int = 0
    avg_queue_time_sec: float = 0.0
    cost_per_shot: float = 0.0
    max_shots: int = 100_000
    is_available: bool = True


@dataclass(frozen=True)
class RoutingConstraints:
    """User-specified constraints for backend selection.

    Attributes:
        optimize_for: Primary optimization target.
        max_cost_usd: Maximum acceptable cost in USD.
        min_fidelity: Minimum acceptable fidelity (0-1).
        max_queue_time_sec: Maximum acceptable queue wait time.
        preferred_providers: If set, only consider these providers.
        exclude_simulators: If True, only route to real QPUs.
    """

    optimize_for: str = "quality"
    max_cost_usd: float | None = None
    min_fidelity: float | None = None
    max_queue_time_sec: float | None = None
    preferred_providers: frozenset[str] | None = None
    exclude_simulators: bool = False


@dataclass(frozen=True)
class RoutingDecision:
    """The result of a routing decision.

    Attributes:
        backend: Selected backend name.
        reason: Human-readable explanation of the decision.
        scores: Per-backend composite scores.
        score_breakdown: Detailed per-factor scores for the selected backend.
        circuit_features: Extracted circuit features.
        constraints: Applied constraints.
        routing_time_ms: Time taken for the routing decision.
    """

    backend: str
    reason: str
    scores: dict[str, float]
    score_breakdown: dict[str, float]
    circuit_features: CircuitFeatures
    constraints: RoutingConstraints
    routing_time_ms: float


@dataclass(frozen=True)
class RoutingLog:
    """Structured log entry for QuantRouter training data collection.

    Matches the data collection schema from Phase 1 Implementation Plan,
    Section 3.2 (Week 8-12: QuantRouter v0.1 Design).
    """

    timestamp: str
    circuit_features: dict[str, Any]
    backend_selected: str
    user_constraints: dict[str, Any]
    routing_decision: dict[str, Any]


# ─── Scoring Factors ───

# Default weights for scoring (sum to 1.0)
DEFAULT_WEIGHTS: dict[str, float] = {
    "qubit_compatibility": 0.25,
    "connectivity_match": 0.20,
    "gate_fidelity": 0.20,
    "queue_time": 0.15,
    "cost": 0.10,
    "historical_success": 0.10,
}

# Weight overrides per optimization target
_QUALITY_WEIGHTS: dict[str, float] = {
    "qubit_compatibility": 0.20,
    "connectivity_match": 0.25,
    "gate_fidelity": 0.30,
    "queue_time": 0.05,
    "cost": 0.05,
    "historical_success": 0.15,
}

_SPEED_WEIGHTS: dict[str, float] = {
    "qubit_compatibility": 0.20,
    "connectivity_match": 0.10,
    "gate_fidelity": 0.10,
    "queue_time": 0.40,
    "cost": 0.05,
    "historical_success": 0.15,
}

_COST_WEIGHTS: dict[str, float] = {
    "qubit_compatibility": 0.20,
    "connectivity_match": 0.10,
    "gate_fidelity": 0.10,
    "queue_time": 0.10,
    "cost": 0.40,
    "historical_success": 0.10,
}


# ─── Circuit Analyzer ───


def analyze_circuit(circuit: Any) -> CircuitFeatures:
    """Extract routing-relevant features from a QuantSDK circuit.

    Args:
        circuit: A ``quantsdk.Circuit`` instance.

    Returns:
        CircuitFeatures with all extracted metrics.
    """
    ops = circuit.count_ops()
    gates = circuit.gates

    # Count by gate type
    single_q = 0
    two_q = 0
    three_q = 0
    measurements = 0
    parameterized = False
    connectivity: set[tuple[int, int]] = set()
    cx_count = 0

    param_gates = {"RX", "RY", "RZ", "U1", "U2", "U3", "P", "R",
                   "CRX", "CRY", "CRZ", "CP", "CU1", "CU3",
                   "RXX", "RYY", "RZZ", "RZX"}

    for gate in gates:
        if gate.name == "MEASURE":
            measurements += 1
            continue
        if gate.name == "BARRIER":
            continue

        nq = gate.num_qubits
        if nq == 1:
            single_q += 1
        elif nq == 2:
            two_q += 1
            q0, q1 = gate.qubits
            connectivity.add((min(q0, q1), max(q0, q1)))
            if gate.name in ("CX", "CY", "CZ", "CH", "SWAP", "iSWAP",
                             "DCX", "ECR", "CS", "CSdg", "CSX",
                             "CRX", "CRY", "CRZ", "CP", "CU1", "CU3",
                             "RXX", "RYY", "RZZ", "RZX"):
                cx_count += 1
        elif nq == 3:
            three_q += 1

        if gate.name in param_gates:
            parameterized = True

    gate_types = frozenset(ops.keys())
    total_gate_count = single_q + two_q + three_q

    # Detect algorithm class
    algorithm_class = _detect_algorithm_class(
        circuit, gate_types, single_q, two_q, parameterized
    )

    return CircuitFeatures(
        qubit_count=circuit.num_qubits,
        gate_count=total_gate_count,
        depth=circuit.depth,
        cx_count=cx_count,
        gate_types=gate_types,
        single_qubit_gates=single_q,
        two_qubit_gates=two_q,
        three_qubit_gates=three_q,
        measurement_count=measurements,
        has_parameterized_gates=parameterized,
        algorithm_class=algorithm_class,
        connectivity=frozenset(connectivity),
    )


def _detect_algorithm_class(
    circuit: Any,
    gate_types: frozenset[str],
    single_q: int,
    two_q: int,
    parameterized: bool,
) -> AlgorithmClass:
    """Heuristic classification of a circuit's algorithm type.

    This is a simple rule-based classifier. The ML model in QuantRouter v0.5
    will replace this with a GNN-based circuit classification.
    """
    n = circuit.num_qubits

    # Bell state: 2 qubits, H + CX
    if n == 2 and "H" in gate_types and "CX" in gate_types and single_q <= 2 and two_q <= 1:
        return AlgorithmClass.BELL_STATE

    # GHZ: n qubits, H on first + CX cascade
    if "H" in gate_types and "CX" in gate_types and two_q == n - 1 and single_q <= 2:
        return AlgorithmClass.GHZ

    # QFT: lots of H + controlled rotations
    if ("H" in gate_types and
            any(g in gate_types for g in ("CP", "CRZ", "CU1")) and
            not parameterized):
        return AlgorithmClass.QFT

    # QAOA: parameterized with RZZ or ZZ-like + RX mixers
    if parameterized and any(g in gate_types for g in ("RZZ", "RXX", "RYY")):
        return AlgorithmClass.QAOA

    # VQE / Variational: parameterized with rotation + entangling layers
    if parameterized and two_q > 0 and any(g in gate_types for g in ("RY", "RZ", "RX")):
        return AlgorithmClass.VARIATIONAL

    # Grover: X, H, CCX (multi-controlled), barrier pattern
    if "CCX" in gate_types and "H" in gate_types:
        return AlgorithmClass.GROVER

    return AlgorithmClass.GENERAL


# ─── QuantRouter ───


# Built-in backend registry (populated with known backends)
_DEFAULT_BACKENDS: list[BackendCapability] = [
    BackendCapability(
        name="local_simulator",
        provider="quantsdk",
        num_qubits=24,
        is_simulator=True,
        native_gates=frozenset(["H", "X", "Y", "Z", "CX", "CZ", "RX", "RY", "RZ", "U3", "SWAP", "CCX"]),
        avg_single_qubit_fidelity=1.0,
        avg_two_qubit_fidelity=1.0,
        queue_depth=0,
        avg_queue_time_sec=0.0,
        cost_per_shot=0.0,
        max_shots=1_000_000,
    ),
    BackendCapability(
        name="aer_simulator",
        provider="qiskit",
        num_qubits=32,
        is_simulator=True,
        native_gates=frozenset(["H", "X", "Y", "Z", "CX", "CZ", "RX", "RY", "RZ", "U3", "SWAP", "CCX"]),
        avg_single_qubit_fidelity=1.0,
        avg_two_qubit_fidelity=1.0,
        queue_depth=0,
        avg_queue_time_sec=0.0,
        cost_per_shot=0.0,
        max_shots=1_000_000,
    ),
    BackendCapability(
        name="ibm_brisbane",
        provider="ibm",
        num_qubits=127,
        is_simulator=False,
        native_gates=frozenset(["CX", "ID", "RZ", "SX", "X"]),
        avg_single_qubit_fidelity=0.9996,
        avg_two_qubit_fidelity=0.99,
        queue_depth=15,
        avg_queue_time_sec=120.0,
        cost_per_shot=0.00035,
        max_shots=100_000,
    ),
    BackendCapability(
        name="ibm_osaka",
        provider="ibm",
        num_qubits=127,
        is_simulator=False,
        native_gates=frozenset(["CX", "ID", "RZ", "SX", "X"]),
        avg_single_qubit_fidelity=0.9995,
        avg_two_qubit_fidelity=0.985,
        queue_depth=8,
        avg_queue_time_sec=90.0,
        cost_per_shot=0.00035,
        max_shots=100_000,
    ),
    BackendCapability(
        name="ibm_kyoto",
        provider="ibm",
        num_qubits=127,
        is_simulator=False,
        native_gates=frozenset(["CX", "ID", "RZ", "SX", "X"]),
        avg_single_qubit_fidelity=0.9994,
        avg_two_qubit_fidelity=0.98,
        queue_depth=25,
        avg_queue_time_sec=180.0,
        cost_per_shot=0.00035,
        max_shots=100_000,
    ),
]


class QuantRouter:
    """Rule-based quantum backend router (v0.1).

    Analyzes a quantum circuit's features and scores available backends
    to select the optimal execution target. Uses a weighted multi-factor
    scoring system based on qubit compatibility, connectivity match,
    gate fidelity, queue time, and cost.

    **Scoring Factors** (weighted, sum to 1.0):

    +-------------------------+--------+
    | Factor                  | Weight |
    +=========================+========+
    | Qubit compatibility     |  0.25  |
    +-------------------------+--------+
    | Connectivity match      |  0.20  |
    +-------------------------+--------+
    | Gate fidelity           |  0.20  |
    +-------------------------+--------+
    | Queue time              |  0.15  |
    +-------------------------+--------+
    | Cost                    |  0.10  |
    +-------------------------+--------+
    | Historical success      |  0.10  |
    +-------------------------+--------+

    Weights shift based on the ``optimize_for`` setting:
    - ``"quality"`` → higher gate_fidelity + connectivity weights
    - ``"speed"`` → higher queue_time weight
    - ``"cost"`` → higher cost weight

    Example::

        from quantsdk.router import QuantRouter, RoutingConstraints

        router = QuantRouter()
        decision = router.route(circuit)
        print(decision.backend)  # "local_simulator"

        # With constraints
        decision = router.route(circuit, constraints=RoutingConstraints(
            optimize_for="quality",
            exclude_simulators=True,
        ))
    """

    def __init__(
        self,
        backends: list[BackendCapability] | None = None,
        weights: dict[str, float] | None = None,
    ) -> None:
        """Initialize the router.

        Args:
            backends: Available backends. Defaults to built-in registry.
            weights: Custom scoring weights. Defaults to DEFAULT_WEIGHTS.
        """
        self._backends = list(backends or _DEFAULT_BACKENDS)
        self._weights = dict(weights or DEFAULT_WEIGHTS)
        self._routing_log: list[RoutingLog] = []

    @property
    def backends(self) -> list[BackendCapability]:
        """Currently registered backends."""
        return list(self._backends)

    @property
    def routing_log(self) -> list[RoutingLog]:
        """Routing decisions log (for ML training data collection)."""
        return list(self._routing_log)

    def register_backend(self, backend: BackendCapability) -> None:
        """Register a new backend for routing consideration.

        Args:
            backend: Backend capability description.
        """
        # Replace existing backend with the same name
        self._backends = [b for b in self._backends if b.name != backend.name]
        self._backends.append(backend)
        logger.info("Registered backend: %s (%s, %d qubits)",
                     backend.name, backend.provider, backend.num_qubits)

    def update_backend(self, name: str, **updates: Any) -> None:
        """Update a backend's dynamic properties (queue depth, availability).

        Args:
            name: Backend name to update.
            **updates: Fields to update (queue_depth, avg_queue_time_sec, is_available).
        """
        for i, b in enumerate(self._backends):
            if b.name == name:
                # Create a new BackendCapability with updated fields
                from dataclasses import asdict
                current = asdict(b)
                current.update(updates)
                self._backends[i] = BackendCapability(
                    name=str(current["name"]),
                    provider=str(current["provider"]),
                    num_qubits=int(current["num_qubits"]),
                    is_simulator=bool(current["is_simulator"]),
                    native_gates=frozenset(current["native_gates"]),
                    avg_single_qubit_fidelity=float(current["avg_single_qubit_fidelity"]),
                    avg_two_qubit_fidelity=float(current["avg_two_qubit_fidelity"]),
                    queue_depth=int(current["queue_depth"]),
                    avg_queue_time_sec=float(current["avg_queue_time_sec"]),
                    cost_per_shot=float(current["cost_per_shot"]),
                    max_shots=int(current["max_shots"]),
                    is_available=bool(current["is_available"]),
                )
                return
        raise ValueError(f"Backend '{name}' not found in registry")

    def route(
        self,
        circuit: Any,
        constraints: RoutingConstraints | None = None,
    ) -> RoutingDecision:
        """Select the optimal backend for a circuit.

        This implements the rule-based routing decision tree from the
        Phase 1 Implementation Plan (Section 3.2).

        Args:
            circuit: A QuantSDK Circuit instance.
            constraints: Optional routing constraints.

        Returns:
            RoutingDecision with the selected backend and explanation.

        Raises:
            ValueError: If no suitable backend is found.
        """
        start = time.monotonic()
        constraints = constraints or RoutingConstraints()

        # Step 1: Analyze circuit
        features = analyze_circuit(circuit)
        logger.debug("Circuit analysis: %s", features)

        # Step 2: Get weights based on optimization target
        weights = self._get_weights(constraints.optimize_for)

        # Step 3: Filter available backends
        candidates = self._filter_backends(features, constraints)
        if not candidates:
            raise ValueError(
                f"No suitable backend found for {features.qubit_count}-qubit circuit "
                f"with constraints: {constraints}. "
                f"Consider relaxing constraints or registering additional backends."
            )

        # Step 4: Score each candidate
        scores: dict[str, float] = {}
        breakdowns: dict[str, dict[str, float]] = {}
        for backend in candidates:
            score, breakdown = self._score_backend(features, backend, weights)
            scores[backend.name] = round(score, 4)
            breakdowns[backend.name] = breakdown

        # Step 5: Select the best
        best_name = max(scores, key=scores.get)  # type: ignore[arg-type]
        best_breakdown = breakdowns[best_name]

        # Step 6: Generate human-readable reason
        reason = self._explain_decision(features, best_name, best_breakdown, constraints)

        elapsed_ms = (time.monotonic() - start) * 1000

        decision = RoutingDecision(
            backend=best_name,
            reason=reason,
            scores=scores,
            score_breakdown=best_breakdown,
            circuit_features=features,
            constraints=constraints,
            routing_time_ms=round(elapsed_ms, 2),
        )

        # Step 7: Log for training data
        self._log_decision(decision)

        logger.info("Routed %d-qubit circuit to '%s' (score=%.4f) in %.1fms",
                     features.qubit_count, best_name, scores[best_name], elapsed_ms)

        return decision

    def _get_weights(self, optimize_for: str) -> dict[str, float]:
        """Get scoring weights based on optimization target."""
        weights_map = {
            "quality": _QUALITY_WEIGHTS,
            "speed": _SPEED_WEIGHTS,
            "cost": _COST_WEIGHTS,
        }
        return weights_map.get(optimize_for, self._weights)

    def _filter_backends(
        self,
        features: CircuitFeatures,
        constraints: RoutingConstraints,
    ) -> list[BackendCapability]:
        """Filter backends that can't run this circuit."""
        candidates = []
        for b in self._backends:
            # Must be available
            if not b.is_available:
                continue

            # Must have enough qubits
            if b.num_qubits < features.qubit_count:
                continue

            # Simulator exclusion
            if constraints.exclude_simulators and b.is_simulator:
                continue

            # Provider filter
            if constraints.preferred_providers and b.provider not in constraints.preferred_providers:
                continue

            # Cost filter
            if constraints.max_cost_usd is not None:
                estimated_cost = b.cost_per_shot * 1024  # Assume default shots
                if estimated_cost > constraints.max_cost_usd:
                    continue

            # Queue time filter
            if constraints.max_queue_time_sec is not None and b.avg_queue_time_sec > constraints.max_queue_time_sec:
                continue

            candidates.append(b)

        return candidates

    def _score_backend(
        self,
        features: CircuitFeatures,
        backend: BackendCapability,
        weights: dict[str, float],
    ) -> tuple[float, dict[str, float]]:
        """Score a backend for a circuit. Returns (total_score, breakdown)."""

        breakdown: dict[str, float] = {}

        # 1. Qubit compatibility (0-1)
        # Perfect if backend has exactly enough or slightly more qubits
        if backend.num_qubits >= features.qubit_count:
            ratio = features.qubit_count / backend.num_qubits
            # Prefer backends where circuit uses 10-80% of qubits
            if 0.1 <= ratio <= 0.8:
                qubit_score = 1.0
            elif ratio > 0.8:
                qubit_score = 0.9  # Circuit uses most of backend — tighter margins
            else:
                qubit_score = 0.7  # Very small circuit on large backend
        else:
            qubit_score = 0.0  # Can't run
        breakdown["qubit_compatibility"] = round(qubit_score, 4)

        # 2. Connectivity match (0-1)
        # Simulators have perfect connectivity
        if backend.is_simulator:
            conn_score = 1.0
        elif not features.connectivity:
            conn_score = 1.0  # No 2-qubit gates → no connectivity needed
        else:
            # Heuristic: penalize based on ratio of 2-qubit gates to backend qubits
            # Real implementation would check actual topology graph embedding
            entangling_density = features.two_qubit_gates / max(features.gate_count, 1)
            # Higher fidelity backends handle dense entanglement better
            conn_score = max(0.3, 1.0 - entangling_density * (1 - backend.avg_two_qubit_fidelity) * 10)
        breakdown["connectivity_match"] = round(conn_score, 4)

        # 3. Gate fidelity (0-1)
        if backend.is_simulator:
            fidelity_score = 1.0
        else:
            # Weighted by gate mix
            single_ratio = features.single_qubit_gates / max(features.gate_count, 1)
            two_ratio = features.two_qubit_gates / max(features.gate_count, 1)
            fidelity_score = (
                single_ratio * backend.avg_single_qubit_fidelity
                + two_ratio * backend.avg_two_qubit_fidelity
                + (1 - single_ratio - two_ratio) * 0.95  # Default for 3-qubit
            )
            # Amplify by circuit depth (deeper = more noise accumulation)
            depth_penalty = max(0.0, 1.0 - features.depth * 0.002)
            fidelity_score *= depth_penalty
        breakdown["gate_fidelity"] = round(min(1.0, fidelity_score), 4)

        # 4. Queue time (0-1, higher is better = shorter queue)
        if backend.avg_queue_time_sec <= 1.0:
            queue_score = 1.0
        else:
            # Inverse relationship: 0s → 1.0, 60s → 0.5, 300s → 0.2
            queue_score = 1.0 / (1.0 + backend.avg_queue_time_sec / 60.0)
        breakdown["queue_time"] = round(queue_score, 4)

        # 5. Cost (0-1, higher is better = cheaper)
        if backend.cost_per_shot <= 0.0:
            cost_score = 1.0  # Free
        else:
            # Inverse: $0 → 1.0, $0.001/shot → ~0.5
            cost_score = 1.0 / (1.0 + backend.cost_per_shot * 1000)
        breakdown["cost"] = round(cost_score, 4)

        # 6. Historical success (0-1)
        # In v0.1, use a static heuristic. v0.5 will use actual execution data.
        if backend.is_simulator:
            hist_score = 0.95  # Simulators are reliable but don't represent real hardware
        else:
            # Assume correlated with fidelity
            hist_score = (backend.avg_single_qubit_fidelity + backend.avg_two_qubit_fidelity) / 2
        breakdown["historical_success"] = round(hist_score, 4)

        # Weighted sum
        total = sum(weights[k] * breakdown[k] for k in weights)

        return total, breakdown

    def _explain_decision(
        self,
        features: CircuitFeatures,
        backend_name: str,
        breakdown: dict[str, float],
        constraints: RoutingConstraints,
    ) -> str:
        """Generate a human-readable explanation."""
        top_factor = max(breakdown, key=breakdown.get)  # type: ignore[arg-type]
        factor_names = {
            "qubit_compatibility": "qubit compatibility",
            "connectivity_match": "connectivity match",
            "gate_fidelity": "gate fidelity",
            "queue_time": "low queue time",
            "cost": "low cost",
            "historical_success": "historical reliability",
        }

        parts = [f"Selected '{backend_name}' for {features.qubit_count}-qubit"]
        if features.algorithm_class != AlgorithmClass.GENERAL:
            parts.append(f"{features.algorithm_class.value}")
        parts.append("circuit")

        reason = " ".join(parts) + "."
        reason += f" Best {factor_names.get(top_factor, top_factor)} score"

        if constraints.optimize_for != "quality":
            reason += f" (optimizing for {constraints.optimize_for})"

        reason += "."
        return reason

    def _log_decision(self, decision: RoutingDecision) -> None:
        """Log routing decision for training data collection."""
        import datetime

        features = decision.circuit_features
        log = RoutingLog(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            circuit_features={
                "qubit_count": features.qubit_count,
                "gate_count": features.gate_count,
                "depth": features.depth,
                "cx_count": features.cx_count,
                "gate_types": sorted(features.gate_types),
                "algorithm_class": features.algorithm_class.value,
            },
            backend_selected=decision.backend,
            user_constraints={
                "optimize_for": decision.constraints.optimize_for,
                "max_cost_usd": decision.constraints.max_cost_usd,
                "min_fidelity": decision.constraints.min_fidelity,
            },
            routing_decision={
                "scores": decision.scores,
                "score_breakdown": decision.score_breakdown,
                "reason": decision.reason,
                "routing_time_ms": decision.routing_time_ms,
            },
        )
        self._routing_log.append(log)

    def export_training_data(self) -> list[dict[str, Any]]:
        """Export routing logs as dictionaries for ML training.

        Returns:
            List of routing decision logs as dicts.
        """
        return [
            {
                "timestamp": log.timestamp,
                "circuit_features": log.circuit_features,
                "backend_selected": log.backend_selected,
                "user_constraints": log.user_constraints,
                "routing_decision": log.routing_decision,
            }
            for log in self._routing_log
        ]
