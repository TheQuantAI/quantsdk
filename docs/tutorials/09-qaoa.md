# Tutorial 9: QAOA

**Time:** 30 minutes  
**Level:** Advanced  
**Concepts:** Combinatorial optimization, problem Hamiltonian, mixer Hamiltonian

!!! tip "Try it interactively"
    This tutorial is also available as a Jupyter notebook you can run locally:  
    [:material-notebook: Open `16_qaoa_maxcut.ipynb`](https://github.com/TheQuantAI/quantsdk/blob/main/examples/16_qaoa_maxcut.ipynb){ .md-button }

## What is QAOA?

The **Quantum Approximate Optimization Algorithm** (QAOA) finds approximate
solutions to combinatorial optimization problems like MaxCut, graph coloring,
and scheduling.

## The MaxCut Problem

Given a graph, partition vertices into two sets to maximize the number of
edges *between* the sets.

## QAOA Circuit Structure

QAOA alternates between two operations $p$ times:

1. **Problem unitary** $U_C(\gamma)$ — encodes the cost function
2. **Mixer unitary** $U_M(\beta)$ — explores the solution space

$$|\gamma, \beta\rangle = U_M(\beta_p) U_C(\gamma_p) \cdots U_M(\beta_1) U_C(\gamma_1) |+\rangle^n$$

## Implementation: MaxCut on a Triangle

```python
import quantsdk as qs
import math

def qaoa_maxcut(gamma: float, beta: float, edges: list) -> qs.Circuit:
    """Build a QAOA circuit for MaxCut.

    Args:
        gamma: Problem parameter.
        beta: Mixer parameter.
        edges: List of (i, j) edges in the graph.
    """
    # Determine number of qubits
    n = max(max(e) for e in edges) + 1
    circuit = qs.Circuit(n, name="qaoa-maxcut")

    # Initial superposition
    for i in range(n):
        circuit.h(i)

    # Problem unitary: exp(-i * gamma * C)
    # For MaxCut: C = sum_{(i,j)} (1 - Z_i Z_j) / 2
    for i, j in edges:
        circuit.cx(i, j)
        circuit.rz(j, 2 * gamma)
        circuit.cx(i, j)

    # Mixer unitary: exp(-i * beta * B)
    # B = sum_i X_i
    for i in range(n):
        circuit.rx(i, 2 * beta)

    circuit.measure_all()
    return circuit

# Triangle graph: 0-1, 1-2, 0-2
edges = [(0, 1), (1, 2), (0, 2)]

# Single QAOA layer
circuit = qaoa_maxcut(gamma=math.pi/4, beta=math.pi/8, edges=edges)
result = qs.run(circuit, shots=4096)

print("MaxCut results (triangle graph):")
for bitstring, count in sorted(result.counts.items(), key=lambda x: -x[1]):
    # Count edges cut
    cuts = sum(1 for i, j in edges if bitstring[i] != bitstring[j])
    print(f"  {bitstring}: {count} shots, {cuts} edges cut")
```

## Multi-Layer QAOA

More layers = better approximation:

```python
def qaoa_multilayer(gammas: list, betas: list, edges: list) -> qs.Circuit:
    """Build a p-layer QAOA circuit."""
    p = len(gammas)
    n = max(max(e) for e in edges) + 1
    circuit = qs.Circuit(n, name=f"qaoa-p{p}")

    # Initial superposition
    for i in range(n):
        circuit.h(i)

    # p layers
    for layer in range(p):
        # Problem unitary
        for i, j in edges:
            circuit.cx(i, j)
            circuit.rz(j, 2 * gammas[layer])
            circuit.cx(i, j)

        # Mixer
        for i in range(n):
            circuit.rx(i, 2 * betas[layer])

    circuit.measure_all()
    return circuit

# 2-layer QAOA
circuit = qaoa_multilayer(
    gammas=[0.8, 0.4],
    betas=[0.5, 0.3],
    edges=edges
)
result = qs.run(circuit, shots=4096)
print(f"Best cut: {result.most_likely}")
```

## Key Takeaways

1. QAOA maps optimization problems to quantum circuits
2. More layers ($p$) = better approximation, but deeper circuits
3. Parameters ($\gamma, \beta$) are optimized classically (like VQE)
4. At $p \rightarrow \infty$, QAOA converges to the optimal solution
5. Practical for near-term quantum computers

## Next Tutorial

:material-arrow-right: [Hybrid Algorithms](10-hybrid-algorithms.md) — building parameterized quantum-classical loops.
