# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for the local simulator and end-to-end qs.run() API."""


import pytest

import quantsdk as qs
from quantsdk.circuit import Circuit
from quantsdk.result import Result
from quantsdk.simulators.local import LocalSimulator


class TestLocalSimulator:
    """Test the local statevector simulator."""

    def test_bell_state(self):
        """Bell state should produce ~50% |00⟩ and ~50% |11⟩."""
        c = Circuit(2)
        c.h(0).cx(0, 1).measure_all()

        sim = LocalSimulator()
        result = sim.run(c, shots=10_000, seed=42)

        assert set(result.counts.keys()) == {"00", "11"}
        assert result.shots == 10_000
        # Each outcome should be close to 50%
        for count in result.counts.values():
            assert 4000 < count < 6000

    def test_x_gate_flips_to_one(self):
        """|0⟩ → X → |1⟩ should always measure 1."""
        c = Circuit(1)
        c.x(0).measure_all()

        sim = LocalSimulator()
        result = sim.run(c, shots=100, seed=42)

        assert result.counts == {"1": 100}

    def test_identity_stays_zero(self):
        """|0⟩ → I → |0⟩ should always measure 0."""
        c = Circuit(1)
        c.i(0).measure_all()

        sim = LocalSimulator()
        result = sim.run(c, shots=100, seed=42)

        assert result.counts == {"0": 100}

    def test_ghz_state(self):
        """3-qubit GHZ state: ~50% |000⟩ and ~50% |111⟩."""
        c = Circuit(3)
        c.h(0).cx(0, 1).cx(1, 2).measure_all()

        sim = LocalSimulator()
        result = sim.run(c, shots=10_000, seed=42)

        assert set(result.counts.keys()) == {"000", "111"}

    def test_seed_reproducibility(self):
        """Same seed should produce identical results."""
        c = Circuit(2)
        c.h(0).cx(0, 1).measure_all()

        sim = LocalSimulator()
        r1 = sim.run(c, shots=1000, seed=123)
        r2 = sim.run(c, shots=1000, seed=123)

        assert r1.counts == r2.counts

    def test_different_seeds_differ(self):
        """Different seeds should (very likely) produce different results."""
        c = Circuit(2)
        c.h(0).cx(0, 1).measure_all()

        sim = LocalSimulator()
        r1 = sim.run(c, shots=1000, seed=1)
        r2 = sim.run(c, shots=1000, seed=2)

        # Very unlikely to be identical with different seeds
        assert r1.counts != r2.counts

    def test_result_metadata(self):
        """Result should contain backend metadata."""
        c = Circuit(2)
        c.h(0).measure_all()

        sim = LocalSimulator()
        result = sim.run(c, shots=100, seed=42)

        assert result.backend == "local_simulator"
        assert result.job_id.startswith("local-")
        assert result.metadata["simulator"] == "quantsdk_local"
        assert result.metadata["num_qubits"] == 2

    def test_too_many_qubits_raises(self):
        """Circuits exceeding MAX_QUBITS should raise an error."""
        c = Circuit(30)
        sim = LocalSimulator()
        with pytest.raises(ValueError, match="local simulator supports at most"):
            sim.run(c, shots=1)

    def test_barrier_has_no_effect(self):
        """Barriers should not affect simulation results."""
        c1 = Circuit(2)
        c1.h(0).cx(0, 1).measure_all()

        c2 = Circuit(2)
        c2.h(0).barrier().cx(0, 1).measure_all()

        sim = LocalSimulator()
        r1 = sim.run(c1, shots=5000, seed=42)
        r2 = sim.run(c2, shots=5000, seed=42)

        assert r1.counts == r2.counts


class TestRunAPI:
    """Test the top-level qs.run() function."""

    def test_run_default_backend(self):
        """qs.run() with no backend should use local simulator."""
        c = qs.Circuit(2)
        c.h(0).cx(0, 1).measure_all()

        result = qs.run(c, shots=1000, seed=42)

        assert isinstance(result, qs.Result)
        assert result.backend == "local_simulator"
        assert result.shots == 1000
        assert set(result.counts.keys()) == {"00", "11"}

    def test_run_explicit_local_simulator(self):
        """qs.run(backend='local_simulator') should work."""
        c = qs.Circuit(1)
        c.x(0).measure_all()

        result = qs.run(c, backend="local_simulator", shots=100, seed=42)
        assert result.counts == {"1": 100}

    def test_run_unknown_backend_raises(self):
        """Requesting an unavailable backend should raise NotImplementedError."""
        c = qs.Circuit(1)
        c.h(0).measure_all()

        with pytest.raises(NotImplementedError, match="not available"):
            qs.run(c, backend="ibm_brisbane")

    def test_run_smart_routing_raises(self):
        """optimize_for should raise NotImplementedError in v0.1."""
        c = qs.Circuit(1)
        c.h(0).measure_all()

        with pytest.raises(NotImplementedError, match="TheQuantCloud"):
            qs.run(c, optimize_for="quality")


class TestResult:
    """Test Result class properties and methods."""

    def test_probabilities(self):
        r = Result(counts={"00": 600, "11": 400}, shots=1000)
        probs = r.probabilities
        assert abs(probs["00"] - 0.6) < 1e-10
        assert abs(probs["11"] - 0.4) < 1e-10

    def test_most_likely(self):
        r = Result(counts={"00": 600, "11": 400}, shots=1000)
        assert r.most_likely == "00"

    def test_most_likely_empty_raises(self):
        r = Result(counts={}, shots=0)
        with pytest.raises(ValueError):
            _ = r.most_likely

    def test_num_qubits(self):
        r = Result(counts={"000": 500, "111": 500}, shots=1000)
        assert r.num_qubits == 3

    def test_get_probability(self):
        r = Result(counts={"0": 700, "1": 300}, shots=1000)
        assert abs(r.get_probability("0") - 0.7) < 1e-10
        assert abs(r.get_probability("1") - 0.3) < 1e-10
        assert r.get_probability("missing") == 0.0

    def test_top_k(self):
        r = Result(counts={"00": 600, "01": 200, "10": 150, "11": 50}, shots=1000)
        top = r.top_k(2)
        assert len(top) == 2
        assert top[0][0] == "00"
        assert top[1][0] == "01"

    def test_to_dict(self):
        r = Result(counts={"0": 1000}, shots=1000, backend="test")
        d = r.to_dict()
        assert d["counts"] == {"0": 1000}
        assert d["shots"] == 1000
        assert d["backend"] == "test"
        assert d["most_likely"] == "0"

    def test_summary(self):
        r = Result(counts={"00": 500, "11": 500}, shots=1000)
        s = r.summary()
        assert "1000" in s
        assert "00" in s

    def test_repr(self):
        r = Result(counts={"0": 100}, shots=100, backend="test")
        assert "test" in repr(r)
