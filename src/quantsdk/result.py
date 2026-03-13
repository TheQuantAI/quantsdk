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

    def to_pandas(self) -> Any:
        """Export result as a pandas DataFrame.

        Requires: ``pip install pandas``

        Returns:
            A ``pandas.DataFrame`` with columns: bitstring, count, probability.

        Example::

            result = qs.run(circuit, shots=1000)
            df = result.to_pandas()
            print(df.head())
        """
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError(
                "pandas is required for to_pandas(). Install it with: pip install pandas"
            ) from e

        rows = [
            {"bitstring": bs, "count": c, "probability": c / self.shots}
            for bs, c in sorted(self.counts.items(), key=lambda x: x[1], reverse=True)
        ]
        return pd.DataFrame(rows)

    # ─── Visualization ───

    def plot_histogram(
        self,
        *,
        top_k: int | None = None,
        title: str | None = None,
        figsize: tuple[float, float] = (10, 5),
        color: str = "#4C72B0",
        show: bool = True,
    ) -> Any:
        """Plot a histogram of measurement results.

        Requires: ``pip install matplotlib``

        Args:
            top_k: Show only the top-k most frequent outcomes. Default: all.
            title: Plot title. Default: "Measurement Results ({shots} shots)".
            figsize: Figure size as (width, height) in inches.
            color: Bar color (any matplotlib color string).
            show: Whether to call ``plt.show()``. Set False for programmatic use.

        Returns:
            A ``matplotlib.figure.Figure`` object.

        Example::

            result = qs.run(circuit, shots=1000)
            result.plot_histogram(top_k=10, title="Bell State")
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            raise ImportError(
                "matplotlib is required for plot_histogram(). "
                "Install it with: pip install thequantsdk[viz]"
            ) from e

        # Sort by count descending
        sorted_items = sorted(self.counts.items(), key=lambda x: x[1], reverse=True)
        if top_k is not None:
            sorted_items = sorted_items[:top_k]

        bitstrings = [bs for bs, _ in sorted_items]
        counts = [c for _, c in sorted_items]
        probs = [c / self.shots for c in counts]

        fig, ax = plt.subplots(figsize=figsize)
        bars = ax.bar(range(len(bitstrings)), probs, color=color, edgecolor="white")
        ax.set_xticks(range(len(bitstrings)))
        ax.set_xticklabels(bitstrings, rotation=45 if len(bitstrings) > 8 else 0, ha="right")
        ax.set_xlabel("Measurement Outcome")
        ax.set_ylabel("Probability")
        ax.set_title(title or f"Measurement Results ({self.shots:,} shots)")
        ax.set_ylim(0, max(probs) * 1.15 if probs else 1.0)

        # Add count labels on bars
        for bar, count, _prob in zip(bars, counts, probs, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{count}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        fig.tight_layout()
        if show:
            plt.show()
        return fig

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
            lines.append(
                f"  Most likely: '{self.most_likely}' "
                f"(p={self.get_probability(self.most_likely):.4f})"
            )
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
