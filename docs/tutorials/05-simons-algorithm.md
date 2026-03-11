# Tutorial 5: Simon's Algorithm

**Time:** 20 minutes  
**Level:** Intermediate  
**Concepts:** Period finding, exponential quantum speedup

!!! tip "Try it interactively"
    This tutorial is also available as a Jupyter notebook you can run locally:  
    [:material-notebook: Open `11_simons_algorithm.ipynb`](https://github.com/TheQuantAI/quantsdk/blob/main/examples/11_simons_algorithm.ipynb){ .md-button }

## The Problem

Given a 2-to-1 function $f: \{0,1\}^n \rightarrow \{0,1\}^n$ with a hidden
period $s$ such that $f(x) = f(y)$ iff $x \oplus y \in \{0^n, s\}$, find $s$.

- **Classical:** $\Omega(2^{n/2})$ queries
- **Quantum:** $O(n)$ queries — exponential speedup!

## Implementation (n=2, s="11")

```python
import quantsdk as qs

n = 2
circuit = qs.Circuit(2 * n, name="simons-algorithm")

# Hadamard on input register
for i in range(n):
    circuit.h(i)

# Oracle for s = "11"
# f maps: 00->00, 01->01, 10->01, 11->00
circuit.barrier()
circuit.cx(0, 2)
circuit.cx(1, 3)
# Apply XOR with s on second input
circuit.cx(0, 3)
circuit.cx(1, 2)
circuit.barrier()

# Hadamard on input register
for i in range(n):
    circuit.h(i)

# Measure input register
for i in range(n):
    circuit.measure(i)

result = qs.run(circuit, shots=1000)
print(result.counts)
# Should see '00' and '11' — both satisfy s.y = 0 (mod 2)
```

## How It Works

1. Run the quantum subroutine $O(n)$ times
2. Each run gives a random $y$ satisfying $s \cdot y = 0 \pmod{2}$
3. Collect $n-1$ linearly independent equations
4. Solve the linear system classically to find $s$

## Key Takeaways

1. First example of **exponential quantum speedup**
2. Inspired Shor's algorithm for factoring
3. Combines quantum parallelism with classical post-processing
4. Requires $O(n)$ quantum runs + classical linear algebra

## Next Tutorial

:material-arrow-right: [Grover's Search](06-grovers-search.md) — quadratic speedup for unstructured search.
