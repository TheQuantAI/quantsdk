# Tutorial 4: Bernstein-Vazirani Algorithm

**Time:** 15 minutes  
**Level:** Intermediate  
**Concepts:** Hidden string problem, quantum query complexity

!!! tip "Try it interactively"
    This tutorial is also available as a Jupyter notebook you can run locally:  
    [:material-notebook: Open `10_bernstein_vazirani.ipynb`](https://github.com/TheQuantAI/quantsdk/blob/main/examples/10_bernstein_vazirani.ipynb){ .md-button }

## The Problem

Given a black-box function $f(x) = s \cdot x \pmod{2}$ where $s$ is a hidden
$n$-bit string, find $s$.

- **Classical:** Requires $n$ queries
- **Quantum:** Requires **1 query**

## The Algorithm

```python
import quantsdk as qs

# Hidden string to find
secret = "110"
n = len(secret)

circuit = qs.Circuit(n + 1, name="bernstein-vazirani")

# Initialize ancilla
circuit.x(n)

# Hadamard all
for i in range(n + 1):
    circuit.h(i)

# Oracle: CNOT from qubit i to ancilla where secret[i] = '1'
circuit.barrier()
for i, bit in enumerate(secret):
    if bit == '1':
        circuit.cx(i, n)
circuit.barrier()

# Hadamard input qubits
for i in range(n):
    circuit.h(i)

# Measure
for i in range(n):
    circuit.measure(i)

# Run
result = qs.run(circuit, shots=1000)
print(f"Secret: {secret}")
print(f"Result: {result.most_likely}")
# Output: '110' (the secret string!)
```

## How It Works

1. Hadamard creates equal superposition of all inputs
2. The oracle applies phase $(-1)^{s \cdot x}$ via phase kickback
3. Final Hadamard interferes the phases to reveal $s$ directly
4. One measurement gives the exact answer with probability 1

## Key Takeaways

1. A linear speedup from $n$ queries to 1 query
2. Demonstrates **phase kickback** — the oracle's effect appears as phases
3. Generalizes Deutsch-Jozsa to extracting information, not just yes/no

## Next Tutorial

:material-arrow-right: [Simon's Algorithm](05-simons-algorithm.md) — exponential speedup for period finding.
