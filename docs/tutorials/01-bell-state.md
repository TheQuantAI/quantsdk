# Tutorial 1: Bell State

**Time:** 10 minutes  
**Level:** Beginner  
**Concepts:** Superposition, entanglement, measurement

## What You'll Build

A **Bell State** — the simplest example of quantum entanglement. Two qubits
become perfectly correlated: measuring one instantly determines the other.

## Background

The four Bell States are:

$$|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$$

$$|\Phi^-\rangle = \frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$$

$$|\Psi^+\rangle = \frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$$

$$|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$$

We'll create $|\Phi^+\rangle$, the most common Bell State.

## Step 1: Create the Circuit

```python
import quantsdk as qs

circuit = qs.Circuit(2, name="bell-state")
```

We need 2 qubits, both starting in $|0\rangle$.

## Step 2: Apply Hadamard

```python
circuit.h(0)  # Put qubit 0 into superposition
```

After this, qubit 0 is in state $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$,
while qubit 1 is still $|0\rangle$.

Combined state: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$

## Step 3: Apply CNOT

```python
circuit.cx(0, 1)  # Entangle: CNOT with control=0, target=1
```

The CNOT flips qubit 1 when qubit 0 is $|1\rangle$:

- $|00\rangle \rightarrow |00\rangle$ (control is 0, no flip)
- $|10\rangle \rightarrow |11\rangle$ (control is 1, flip target)

Result: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle) = |\Phi^+\rangle$

## Step 4: Measure

```python
circuit.measure_all()
```

## Step 5: Run and Verify

```python
result = qs.run(circuit, shots=1000)
print(result.counts)
# {'00': ~500, '11': ~500}
```

You should see roughly equal counts of `00` and `11`, with no `01` or `10` —
that's entanglement!

## Complete Code

```python
import quantsdk as qs

# Create Bell State |Phi+>
circuit = qs.Circuit(2, name="bell-state")
circuit.h(0).cx(0, 1).measure_all()

# Run
result = qs.run(circuit, shots=1000)

# Analyze
print(f"Counts: {result.counts}")
print(f"Probabilities: {result.probabilities}")
print(f"Most likely: {result.most_likely}")

# Visualize
result.plot_histogram()
```

## Other Bell States

Create all four Bell States by adding gates before measurement:

```python
# |Phi+> = (|00> + |11>) / sqrt(2)
phi_plus = qs.Circuit(2).h(0).cx(0, 1).measure_all()

# |Phi-> = (|00> - |11>) / sqrt(2)
phi_minus = qs.Circuit(2).h(0).cx(0, 1).z(0).measure_all()

# |Psi+> = (|01> + |10>) / sqrt(2)
psi_plus = qs.Circuit(2).h(0).cx(0, 1).x(1).measure_all()

# |Psi-> = (|01> - |10>) / sqrt(2)
psi_minus = qs.Circuit(2).h(0).cx(0, 1).x(1).z(0).measure_all()
```

## Key Takeaways

1. **Hadamard** creates superposition — one qubit in two states at once
2. **CNOT** creates entanglement — correlating two qubits
3. **Measurement** collapses the state — you only see `00` or `11`, never `01` or `10`
4. Entanglement is a **resource** used in teleportation, cryptography, and error correction

## Next Tutorial

:material-arrow-right: [Quantum Teleportation](02-teleportation.md) — use entanglement to "teleport" quantum information.
