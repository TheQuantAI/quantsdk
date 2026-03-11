# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Execution result container for quantum circuit runs.

Provides a rich interface to access counts, probabilities, and
visualize results from quantum circuit execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Result:
    """Result of a quantum circuit execution.

    Contains measurement counts, backend metadata, and convenience methods
    for analysis and visualization.

    Attributes:
        counts: Dictionary mapping bitstring outcomes to their counts.
        shots: Number of shots (measurement repetitions).
        backend: Name of the backend that executed the circuit.
        job_id: Unique identifier for the execution job.
        metadata: Additional backend-specific metadata.
    """

    counts: dict[str, int]
    shots: int
    backend: str = "local_simulator"
    job_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    # ─── Core Properties ───

    @property
    def probabilities(self) -> dict[str, float]:
        """Measurement probabilities (counts normalized to sum = 1.0).

        Returns:
            Dictionary mapping bitstrings to their probability.
        """
        if self.shots == 0:
            return {}
        return {k: v / self.shots for k, v in self.counts.items()}

    @property
    def most_likely(self) -> str:
        """The most frequently measured bitstring.

        Returns:
            The bitstring with the highest count.

        Raises:
            ValueError: If counts are empty.
        """
        if not self.counts:
            raise ValueError("No measurement results available")
        return max(self.counts, key=lambda k: self.counts[k])

    @property
    def num_qubits(self) -> int:
        """Number of qubits (inferred from bitstring length)."""
        if not self.counts:
            return 0
        return len(next(iter(self.counts)))

    # ─── Analysis Methods ───

    def get_probability(self, bitstring: str) -> float:
        """Get the probability of a specific bitstring outcome.

        Args:
            bitstring: The measurement outcome to query.

        Returns:
            Probability as a float (0.0 if bitstring was not observed).
        """
        return self.counts.get(bitstring, 0) / self.shots if self.shots > 0 else 0.0

    def top_k(self, k: int = 5) -> list[tuple[str, int, float]]:
        """Get the top-k most frequent measurement outcomes.

        Args:
            k: Number of top results to return.

        Returns:
            List of (bitstring, count, probability) tuples, sorted by count descending.
        """
        sorted_counts = sorted(self.counts.items(), key=lambda x: x[1], reverse=True)
        return [
            (bitstring, count, count / self.shots if self.shots > 0 else 0.0)
            for bitstring, count in sorted_counts[:k]
        ]

    def expectation_value(self) -> float:
        """Compute the expectation value treating bitstrings as binary numbers.

        Returns:
            Weighted average of bitstring values (as integers).
        """
        if self.shots == 0:
            return 0.0
        total = sum(int(bitstring, 2) * count for bitstring, count in self.counts.items())
        return total / self.shots

    # ─── Export Methods ───

    def to_dict(self) -> dict[str, Any]:
        """Export result as a plain dictionary.

        Returns:
            Dictionary containing all result data.
        """
        return {
            "counts": self.counts,
            "shots": self.shots,
            "backend": self.backend,
            "job_id": self.job_id,
            "probabilities": self.probabilities,
            "most_likely": self.most_likely if self.counts else None,
            "metadata": self.metadata,
        }

    # ─── Display ───

    def summary(self) -> str:
        """Human-readable summary of the result.

        Returns:
            Formatted string with key result information.
        """
        lines = [
            f"Result(backend='{self.backend}', shots={self.shots})",
            f"  Unique outcomes: {len(self.counts)}",
        ]
        if self.counts:
            lines.append(f"  Most likely: '{self.most_likely}' "
                         f"(p={self.get_probability(self.most_likely):.4f})")
            lines.append("  Top results:")
            for bitstring, count, prob in self.top_k(5):
                bar = "█" * int(prob * 40)
                lines.append(f"    '{bitstring}': {count:>6} ({prob:.4f}) {bar}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"Result(counts={dict(list(self.counts.items())[:3])}{'...' if len(self.counts) > 3 else ''}, "
            f"shots={self.shots}, backend='{self.backend}')"
        )

    def __str__(self) -> str:
        return self.summary()
