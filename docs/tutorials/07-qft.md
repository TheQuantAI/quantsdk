# Tutorial 7: Quantum Fourier Transform

**Time:** 25 minutes  
**Level:** Advanced  
**Concepts:** Phase estimation, periodicity, Shor's algorithm foundation

!!! tip "Try it interactively"
    This tutorial is also available as a Jupyter notebook you can run locally:  
    [:material-notebook: Open `13_qft.ipynb`](https://github.com/TheQuantAI/quantsdk/blob/main/examples/13_qft.ipynb){ .md-button }

## What is the QFT?

The Quantum Fourier Transform maps computational basis states to frequency
basis states:

$$QFT|j\rangle = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i jk/N} |k\rangle$$

It's the quantum analog of the classical Discrete Fourier Transform, but
operates on amplitudes in superposition — exponentially faster.

## Implementation (3 qubits)

```python
import quantsdk as qs
import math

n = 3

def qft_circuit(n: int) -> qs.Circuit:
    """Build an n-qubit QFT circuit."""
    circuit = qs.Circuit(n, name=f"qft-{n}")

    for i in range(n):
        # Hadamard on qubit i
        circuit.h(i)

        # Controlled rotations
        for j in range(i + 1, n):
            angle = math.pi / (2 ** (j - i))
            circuit.cp(i, j, angle)

    # Swap qubits to reverse bit order
    for i in range(n // 2):
        circuit.swap(i, n - 1 - i)

    return circuit

# Build QFT
qft = qft_circuit(3)

# Prepare an input state, e.g., |101> = |5>
full_circuit = qs.Circuit(3, name="qft-demo")
full_circuit.x(0).x(2)  # Prepare |101>

# Append QFT gates
for gate, qubits, params in qft.gates:
    # Rebuild gates on the full circuit
    pass

# For simplicity, build directly:
circuit = qs.Circuit(3, name="qft-demo")
circuit.x(0).x(2)  # Input: |101>

# QFT
circuit.h(0)
circuit.cp(0, 1, math.pi / 2)
circuit.cp(0, 2, math.pi / 4)
circuit.h(1)
circuit.cp(1, 2, math.pi / 2)
circuit.h(2)
circuit.swap(0, 2)

circuit.measure_all()

result = qs.run(circuit, shots=1000)
print(result.counts)
```

## The QFT Structure

For $n$ qubits, the QFT circuit consists of:

1. **Hadamard** on each qubit
2. **Controlled phase rotations** $CR_k$ with angle $\frac{2\pi}{2^k}$
3. **SWAP** gates to reverse bit order

Circuit depth: $O(n^2)$ gates — exponentially fewer than the $O(n \cdot 2^n)$
classical FFT.

## Inverse QFT

The inverse QFT is simply the QFT circuit reversed with negated angles:

```python
def inverse_qft(n: int) -> qs.Circuit:
    """Build an n-qubit inverse QFT circuit."""
    circuit = qs.Circuit(n, name=f"iqft-{n}")

    # Reverse the swaps
    for i in range(n // 2):
        circuit.swap(i, n - 1 - i)

    # Reverse the rotations
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, i, -1):
            angle = -math.pi / (2 ** (j - i))
            circuit.cp(i, j, angle)
        circuit.h(i)

    return circuit
```

## Applications

The QFT is a subroutine in:

- **Shor's algorithm** — integer factoring
- **Quantum phase estimation** — finding eigenvalues
- **Hidden subgroup problem** — generalizes many quantum algorithms
- **Quantum counting** — counting solutions to search problems

## Key Takeaways

1. QFT transforms between computational and frequency bases
2. $O(n^2)$ gates vs $O(n \cdot 2^n)$ classical — exponential speedup
3. It's a *subroutine*, not a standalone algorithm
4. The inverse QFT is used more often (in phase estimation)

## Next Tutorial

:material-arrow-right: [VQE](08-vqe.md) — variational quantum eigensolver for chemistry.
