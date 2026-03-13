# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for QuantRouter v0.1 — rule-based quantum backend routing."""

from __future__ import annotations

import pytest

from quantsdk.circuit import Circuit
from quantsdk.router import (
    AlgorithmClass,
    BackendCapability,
    CircuitFeatures,
    OptimizeFor,
    QuantRouter,
    RoutingConstraints,
    RoutingDecision,
    analyze_circuit,
)

# ─── Fixtures ───


@pytest.fixture
def bell_circuit() -> Circuit:
    """Simple 2-qubit Bell state circuit."""
    c = Circuit(2, name="bell")
    c.h(0)
    c.cx(0, 1)
    c.measure_all()
    return c


@pytest.fixture
def ghz_circuit() -> Circuit:
    """3-qubit GHZ state circuit."""
    c = Circuit(3, name="ghz")
    c.h(0)
    c.cx(0, 1)
    c.cx(1, 2)
    c.measure_all()
    return c


@pytest.fixture
def variational_circuit() -> Circuit:
    """Parameterized variational circuit."""
    c = Circuit(4, name="vqe")
    for i in range(4):
        c.ry(i, 0.5)
    c.cx(0, 1)
    c.cx(1, 2)
    c.cx(2, 3)
    for i in range(4):
        c.rz(i, 0.3)
    c.measure_all()
    return c


@pytest.fixture
def deep_circuit() -> Circuit:
    """Deep 5-qubit circuit with many gates."""
    c = Circuit(5, name="deep")
    for _ in range(20):
        for i in range(5):
            c.h(i)
        for i in range(4):
            c.cx(i, i + 1)
    c.measure_all()
    return c


@pytest.fixture
def simple_backends() -> list[BackendCapability]:
    """Small set of backends for testing."""
    return [
        BackendCapability(
            name="sim_cpu",
            provider="quantsdk",
            num_qubits=24,
            is_simulator=True,
            avg_single_qubit_fidelity=1.0,
            avg_two_qubit_fidelity=1.0,
            queue_depth=0,
            avg_queue_time_sec=0.0,
            cost_per_shot=0.0,
        ),
        BackendCapability(
            name="ibm_test",
            provider="ibm",
            num_qubits=127,
            is_simulator=False,
            avg_single_qubit_fidelity=0.999,
            avg_two_qubit_fidelity=0.99,
            queue_depth=10,
            avg_queue_time_sec=120.0,
            cost_per_shot=0.00035,
        ),
        BackendCapability(
            name="ionq_test",
            provider="ionq",
            num_qubits=36,
            is_simulator=False,
            avg_single_qubit_fidelity=0.9999,
            avg_two_qubit_fidelity=0.995,
            queue_depth=5,
            avg_queue_time_sec=60.0,
            cost_per_shot=0.001,
        ),
    ]


@pytest.fixture
def router(simple_backends: list[BackendCapability]) -> QuantRouter:
    """Router with test backends."""
    return QuantRouter(backends=simple_backends)


# ─── Circuit Analysis Tests ───


class TestAnalyzeCircuit:
    """Tests for the circuit feature extraction."""

    def test_bell_state_features(self, bell_circuit: Circuit) -> None:
        features = analyze_circuit(bell_circuit)
        assert features.qubit_count == 2
        assert features.single_qubit_gates == 1  # H
        assert features.two_qubit_gates == 1  # CX
        assert features.measurement_count == 2
        assert features.cx_count == 1
        assert "H" in features.gate_types
        assert "CX" in features.gate_types
        assert features.algorithm_class == AlgorithmClass.BELL_STATE

    def test_ghz_features(self, ghz_circuit: Circuit) -> None:
        features = analyze_circuit(ghz_circuit)
        assert features.qubit_count == 3
        assert features.single_qubit_gates == 1
        assert features.two_qubit_gates == 2
        assert features.cx_count == 2
        assert features.algorithm_class == AlgorithmClass.GHZ

    def test_variational_features(self, variational_circuit: Circuit) -> None:
        features = analyze_circuit(variational_circuit)
        assert features.qubit_count == 4
        assert features.has_parameterized_gates is True
        assert features.two_qubit_gates == 3
        assert features.algorithm_class == AlgorithmClass.VARIATIONAL

    def test_connectivity_tracking(self, variational_circuit: Circuit) -> None:
        features = analyze_circuit(variational_circuit)
        # CX(0,1), CX(1,2), CX(2,3)
        assert (0, 1) in features.connectivity
        assert (1, 2) in features.connectivity
        assert (2, 3) in features.connectivity

    def test_empty_circuit(self) -> None:
        c = Circuit(2)
        features = analyze_circuit(c)
        assert features.qubit_count == 2
        assert features.gate_count == 0
        assert features.depth == 0

    def test_deep_circuit_features(self, deep_circuit: Circuit) -> None:
        features = analyze_circuit(deep_circuit)
        assert features.qubit_count == 5
        assert features.gate_count > 0
        assert features.depth > 0
        assert features.algorithm_class == AlgorithmClass.GENERAL


# ─── QuantRouter Core Tests ───


class TestQuantRouter:
    """Tests for the QuantRouter routing engine."""

    def test_default_router_has_backends(self) -> None:
        router = QuantRouter()
        assert len(router.backends) >= 3

    def test_custom_backends(self, simple_backends: list[BackendCapability]) -> None:
        router = QuantRouter(backends=simple_backends)
        assert len(router.backends) == 3

    def test_route_bell_state(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(bell_circuit)
        assert isinstance(decision, RoutingDecision)
        assert decision.backend in ("sim_cpu", "ibm_test", "ionq_test")
        assert decision.reason
        assert decision.routing_time_ms >= 0

    def test_route_returns_scores(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(bell_circuit)
        assert len(decision.scores) > 0
        for name, score in decision.scores.items():
            assert 0 <= score <= 1, f"Score for {name} out of range: {score}"

    def test_route_score_breakdown(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(bell_circuit)
        expected_factors = {
            "qubit_compatibility",
            "connectivity_match",
            "gate_fidelity",
            "queue_time",
            "cost",
            "historical_success",
        }
        assert set(decision.score_breakdown.keys()) == expected_factors

    def test_small_circuit_prefers_simulator(
        self, router: QuantRouter, bell_circuit: Circuit
    ) -> None:
        """Small circuits should prefer simulators (free, fast, perfect fidelity)."""
        decision = router.route(bell_circuit)
        assert decision.backend == "sim_cpu"

    def test_optimize_for_quality(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(
            bell_circuit,
            constraints=RoutingConstraints(
                optimize_for="quality",
            ),
        )
        assert decision.constraints.optimize_for == "quality"

    def test_optimize_for_speed(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(
            bell_circuit,
            constraints=RoutingConstraints(
                optimize_for="speed",
            ),
        )
        # Simulator should win on speed (zero queue)
        assert decision.backend == "sim_cpu"

    def test_optimize_for_cost(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(
            bell_circuit,
            constraints=RoutingConstraints(
                optimize_for="cost",
            ),
        )
        # Simulator is free
        assert decision.backend == "sim_cpu"

    def test_exclude_simulators(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(
            bell_circuit,
            constraints=RoutingConstraints(
                exclude_simulators=True,
            ),
        )
        assert decision.backend in ("ibm_test", "ionq_test")

    def test_preferred_providers(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(
            bell_circuit,
            constraints=RoutingConstraints(
                preferred_providers=frozenset(["ionq"]),
            ),
        )
        assert decision.backend == "ionq_test"

    def test_no_suitable_backend(self) -> None:
        router = QuantRouter(
            backends=[
                BackendCapability(name="tiny", provider="test", num_qubits=1),
            ]
        )
        c = Circuit(5)
        c.h(0)
        c.measure_all()
        with pytest.raises(ValueError, match="No suitable backend"):
            router.route(c)

    def test_max_cost_filter(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        # Both QPU backends are too expensive: ibm=0.358, ionq=1.024 > 0.001
        with pytest.raises(ValueError, match="No suitable backend"):
            router.route(
                bell_circuit,
                constraints=RoutingConstraints(
                    max_cost_usd=0.001,
                    exclude_simulators=True,
                ),
            )

    def test_max_queue_time_filter(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        decision = router.route(
            bell_circuit,
            constraints=RoutingConstraints(
                max_queue_time_sec=90.0,
                exclude_simulators=True,
            ),
        )
        # ibm_test: 120s > 90s → filtered
        # ionq_test: 60s < 90s → passes
        assert decision.backend == "ionq_test"

    def test_unavailable_backend_filtered(self, simple_backends: list[BackendCapability]) -> None:
        router = QuantRouter(backends=simple_backends)
        router.update_backend("sim_cpu", is_available=False)
        c = Circuit(2)
        c.h(0)
        c.measure_all()
        decision = router.route(c)
        assert decision.backend != "sim_cpu"


# ─── Backend Management Tests ───


class TestBackendManagement:
    """Tests for backend registration and updates."""

    def test_register_backend(self, router: QuantRouter) -> None:
        new_backend = BackendCapability(
            name="rigetti_test",
            provider="rigetti",
            num_qubits=80,
        )
        router.register_backend(new_backend)
        names = [b.name for b in router.backends]
        assert "rigetti_test" in names

    def test_register_replaces_existing(self, router: QuantRouter) -> None:
        updated = BackendCapability(
            name="sim_cpu",
            provider="quantsdk",
            num_qubits=30,  # Updated
            is_simulator=True,
        )
        router.register_backend(updated)
        for b in router.backends:
            if b.name == "sim_cpu":
                assert b.num_qubits == 30
                break

    def test_update_backend(self, router: QuantRouter) -> None:
        router.update_backend("ibm_test", queue_depth=50, avg_queue_time_sec=300.0)
        for b in router.backends:
            if b.name == "ibm_test":
                assert b.queue_depth == 50
                assert b.avg_queue_time_sec == 300.0
                break

    def test_update_nonexistent_raises(self, router: QuantRouter) -> None:
        with pytest.raises(ValueError, match="not found"):
            router.update_backend("nonexistent", queue_depth=5)


# ─── Routing Log Tests ───


class TestRoutingLog:
    """Tests for training data collection."""

    def test_route_logs_decision(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        assert len(router.routing_log) == 0
        router.route(bell_circuit)
        assert len(router.routing_log) == 1

    def test_multiple_routes_accumulate(
        self, router: QuantRouter, bell_circuit: Circuit, ghz_circuit: Circuit
    ) -> None:
        router.route(bell_circuit)
        router.route(ghz_circuit)
        assert len(router.routing_log) == 2

    def test_export_training_data(self, router: QuantRouter, bell_circuit: Circuit) -> None:
        router.route(bell_circuit)
        data = router.export_training_data()
        assert len(data) == 1
        entry = data[0]
        assert "timestamp" in entry
        assert "circuit_features" in entry
        assert "backend_selected" in entry
        assert "user_constraints" in entry
        assert "routing_decision" in entry

    def test_training_data_circuit_features(
        self, router: QuantRouter, bell_circuit: Circuit
    ) -> None:
        router.route(bell_circuit)
        data = router.export_training_data()
        features = data[0]["circuit_features"]
        assert features["qubit_count"] == 2
        assert features["gate_count"] >= 2
        assert "algorithm_class" in features


# ─── CircuitFeatures Tests ───


class TestCircuitFeatures:
    """Tests for the CircuitFeatures dataclass."""

    def test_frozen(self) -> None:
        features = CircuitFeatures(
            qubit_count=2,
            gate_count=3,
            depth=2,
            cx_count=1,
            gate_types=frozenset(["H", "CX"]),
            single_qubit_gates=1,
            two_qubit_gates=1,
            three_qubit_gates=0,
            measurement_count=2,
            has_parameterized_gates=False,
            algorithm_class=AlgorithmClass.BELL_STATE,
            connectivity=frozenset([(0, 1)]),
        )
        with pytest.raises(AttributeError):
            features.qubit_count = 5  # type: ignore[misc]


# ─── Algorithm Classification Tests ───


class TestAlgorithmClassification:
    """Tests for the heuristic algorithm classifier."""

    def test_bell_state_classified(self, bell_circuit: Circuit) -> None:
        features = analyze_circuit(bell_circuit)
        assert features.algorithm_class == AlgorithmClass.BELL_STATE

    def test_ghz_classified(self, ghz_circuit: Circuit) -> None:
        features = analyze_circuit(ghz_circuit)
        assert features.algorithm_class == AlgorithmClass.GHZ

    def test_variational_classified(self, variational_circuit: Circuit) -> None:
        features = analyze_circuit(variational_circuit)
        assert features.algorithm_class == AlgorithmClass.VARIATIONAL

    def test_general_classified(self) -> None:
        c = Circuit(3)
        c.x(0)
        c.y(1)
        c.z(2)
        c.measure_all()
        features = analyze_circuit(c)
        assert features.algorithm_class == AlgorithmClass.GENERAL

    def test_grover_classified(self) -> None:
        c = Circuit(3)
        c.h(0)
        c.h(1)
        c.h(2)
        c.ccx(0, 1, 2)
        c.h(2)
        c.measure_all()
        features = analyze_circuit(c)
        assert features.algorithm_class == AlgorithmClass.GROVER


# ─── OptimizeFor Enum Tests ───


class TestOptimizeForEnum:
    def test_values(self) -> None:
        assert OptimizeFor.QUALITY.value == "quality"
        assert OptimizeFor.SPEED.value == "speed"
        assert OptimizeFor.COST.value == "cost"


# ─── Edge Cases ───


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_single_qubit_circuit(self, router: QuantRouter) -> None:
        c = Circuit(1)
        c.h(0)
        c.measure_all()
        decision = router.route(c)
        assert decision.backend == "sim_cpu"

    def test_circuit_with_only_measurements(self, router: QuantRouter) -> None:
        c = Circuit(2)
        c.measure_all()
        decision = router.route(c)
        assert decision.backend is not None

    def test_circuit_with_barriers(self, router: QuantRouter) -> None:
        c = Circuit(2)
        c.h(0)
        c.barrier()
        c.cx(0, 1)
        c.measure_all()
        decision = router.route(c)
        assert decision.backend is not None

    def test_circuit_with_resets(self, router: QuantRouter) -> None:
        c = Circuit(2)
        c.h(0)
        c.reset(0)
        c.h(0)
        c.cx(0, 1)
        c.measure_all()
        decision = router.route(c)
        assert decision.backend is not None

    def test_large_qubit_circuit_filters_small_backends(self) -> None:
        backends = [
            BackendCapability(name="small_sim", provider="test", num_qubits=5, is_simulator=True),
            BackendCapability(name="big_qpu", provider="test", num_qubits=100),
        ]
        router = QuantRouter(backends=backends)
        c = Circuit(10)
        for i in range(10):
            c.h(i)
        c.measure_all()
        decision = router.route(c)
        assert decision.backend == "big_qpu"
