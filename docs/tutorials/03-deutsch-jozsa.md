# Tutorial 3: Deutsch-Jozsa Algorithm

**Time:** 15 minutes  
**Level:** Beginner  
**Concepts:** Quantum parallelism, oracles, deterministic speedup

## What You'll Build

The **Deutsch-Jozsa algorithm** — the first quantum algorithm to demonstrate
an exponential speedup over classical computation.

## The Problem

Given a black-box function $f: \{0,1\}^n \rightarrow \{0,1\}$ that is either:

- **Constant**: $f(x) = 0$ for all $x$, or $f(x) = 1$ for all $x$
- **Balanced**: $f(x) = 0$ for exactly half of inputs, $f(x) = 1$ for the other half

**Task:** Determine if $f$ is constant or balanced.

- **Classical:** Requires up to $2^{n-1} + 1$ queries (worst case)
- **Quantum:** Requires exactly **1 query** :material-lightning-bolt:

## The Algorithm (n=2)

We'll implement the 2-qubit version with a balanced oracle.

### Step 1: Setup

```python
import quantsdk as qs

# n=2 input qubits + 1 ancilla qubit
n = 2
circuit = qs.Circuit(n + 1, name="deutsch-jozsa")
```

### Step 2: Initialize

Put the ancilla (qubit 2) in $|1\rangle$, then apply Hadamard to all:

```python
# Initialize ancilla to |1>
circuit.x(n)

# Apply Hadamard to all qubits
for i in range(n + 1):
    circuit.h(i)
```

### Step 3: Apply the Oracle

For a balanced function that computes $f(x) = x_0 \oplus x_1$:

```python
circuit.barrier()
# Oracle: f(x) = x0 XOR x1 (balanced function)
circuit.cx(0, n)   # CNOT: x0 -> ancilla
circuit.cx(1, n)   # CNOT: x1 -> ancilla
circuit.barrier()
```

### Step 4: Apply Hadamard and Measure

```python
# Hadamard on input qubits only
for i in range(n):
    circuit.h(i)

# Measure input qubits
for i in range(n):
    circuit.measure(i)
```

### Step 5: Run and Interpret

```python
result = qs.run(circuit, shots=1000)
print(result.counts)
```

**Interpretation:**

- If all input qubits measure `0` (result is `00`) → **Constant**
- If any input qubit measures `1` → **Balanced**

## Complete Code

```python
import quantsdk as qs

n = 2  # number of input qubits

# --- Balanced Oracle ---
circuit = qs.Circuit(n + 1, name="deutsch-jozsa-balanced")

# Initialize ancilla
circuit.x(n)

# Hadamard all qubits
for i in range(n + 1):
    circuit.h(i)

# Oracle: f(x) = x0 XOR x1 (balanced)
circuit.barrier()
circuit.cx(0, n)
circuit.cx(1, n)
circuit.barrier()

# Hadamard input qubits
for i in range(n):
    circuit.h(i)

# Measure
for i in range(n):
    circuit.measure(i)

result = qs.run(circuit, shots=1000)
print(f"Balanced oracle: {result.counts}")
# Should see non-zero results (e.g., '11': 1000) -> BALANCED

# --- Constant Oracle ---
circuit2 = qs.Circuit(n + 1, name="deutsch-jozsa-constant")
circuit2.x(n)
for i in range(n + 1):
    circuit2.h(i)

circuit2.barrier()
# Constant oracle: f(x) = 0 (do nothing)
circuit2.barrier()

for i in range(n):
    circuit2.h(i)
for i in range(n):
    circuit2.measure(i)

result2 = qs.run(circuit2, shots=1000)
print(f"Constant oracle: {result2.counts}")
# Should see '00': 1000 -> CONSTANT
```

## Key Takeaways

1. **Quantum parallelism** evaluates $f$ on all inputs simultaneously
2. The algorithm gives the answer in **one query** — exponential speedup
3. Oracles encode the function as phase kickback on the ancilla
4. This is a *decision problem* speedup, not a search speedup

## Next Tutorial

:material-arrow-right: [Bernstein-Vazirani](04-bernstein-vazirani.md) — find a hidden string with one quantum query.
