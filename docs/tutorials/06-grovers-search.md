# Tutorial 6: Grover's Search

**Time:** 20 minutes  
**Level:** Intermediate  
**Concepts:** Amplitude amplification, oracle design, quadratic speedup

!!! tip "Try it interactively"
    This tutorial is also available as a Jupyter notebook you can run locally:  
    [:material-notebook: Open `12_grovers_search.ipynb`](https://github.com/TheQuantAI/quantsdk/blob/main/examples/12_grovers_search.ipynb){ .md-button }

## The Problem

Search an unsorted database of $N = 2^n$ items for a marked item.

- **Classical:** $O(N)$ queries
- **Quantum (Grover):** $O(\sqrt{N})$ queries — quadratic speedup

## The Algorithm

Grover's algorithm uses two key operations repeated $\sim\frac{\pi}{4}\sqrt{N}$ times:

1. **Oracle** — marks the target state by flipping its phase
2. **Diffusion** — amplifies the amplitude of the marked state

## Implementation (n=2, target=|11>)

```python
import quantsdk as qs
import math

n = 2
N = 2**n
target = "11"  # We're searching for |11>

# Number of Grover iterations
num_iterations = int(math.pi / 4 * math.sqrt(N))

circuit = qs.Circuit(n, name="grovers-search")

# Step 1: Initialize superposition
for i in range(n):
    circuit.h(i)

# Step 2: Grover iterations
for _ in range(num_iterations):
    # --- Oracle: flip phase of |11> ---
    circuit.cz(0, 1)

    # --- Diffusion operator ---
    for i in range(n):
        circuit.h(i)
    for i in range(n):
        circuit.x(i)
    circuit.cz(0, 1)  # Multi-controlled Z
    for i in range(n):
        circuit.x(i)
    for i in range(n):
        circuit.h(i)

# Step 3: Measure
circuit.measure_all()

# Run
result = qs.run(circuit, shots=1000)
print(f"Searching for: {target}")
print(f"Found: {result.most_likely}")
print(f"Counts: {result.counts}")
# Should find '11' with high probability
```

## How It Works

### Oracle ($U_f$)
Flips the sign of the target state: $|x\rangle \rightarrow (-1)^{f(x)}|x\rangle$

### Diffusion ($U_s$)
Reflects all amplitudes about the mean: $U_s = 2|s\rangle\langle s| - I$

where $|s\rangle = H^{\otimes n}|0\rangle^{\otimes n}$ is the uniform superposition.

### Geometric Interpretation

Think of it as rotating a vector in 2D space:

- The two axes are: "target state" and "non-target states"
- Each iteration rotates by angle $\theta = 2\arcsin(1/\sqrt{N})$
- After $\sim\frac{\pi}{4}\sqrt{N}$ rotations, we're aligned with the target

## 3-Qubit Example

Search among 8 items for $|101\rangle$:

```python
import quantsdk as qs

circuit = qs.Circuit(3, name="grover-3qubit")

# Superposition
circuit.h(0).h(1).h(2)

# Grover iteration (2 iterations for n=3)
for _ in range(2):
    # Oracle for |101>: flip qubits that should be |0>, apply CCZ, flip back
    circuit.x(1)        # Flip qubit 1 (should be 0 in target)
    circuit.ccz(0, 1, 2)  # Multi-controlled Z
    circuit.x(1)        # Unflip

    # Diffusion
    circuit.h(0).h(1).h(2)
    circuit.x(0).x(1).x(2)
    circuit.ccz(0, 1, 2)
    circuit.x(0).x(1).x(2)
    circuit.h(0).h(1).h(2)

circuit.measure_all()

result = qs.run(circuit, shots=1000)
print(f"Most likely: {result.most_likely}")  # Should be '101'
```

## Key Takeaways

1. **Quadratic speedup** — $O(\sqrt{N})$ vs $O(N)$
2. The oracle only needs to *recognize* the answer, not compute it
3. Too many iterations *overshoot* — you rotate past the target
4. Works for any search/SAT problem with a verifiable solution
5. Used as a subroutine in many advanced quantum algorithms

## Next Tutorial

:material-arrow-right: [Quantum Fourier Transform](07-qft.md) — the foundation of Shor's algorithm.
