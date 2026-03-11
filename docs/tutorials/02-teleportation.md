# Tutorial 2: Quantum Teleportation

**Time:** 15 minutes  
**Level:** Beginner  
**Concepts:** Entanglement, classical communication, Bell measurement

!!! tip "Try it interactively"
    This tutorial is also available as a Jupyter notebook you can run locally:  
    [:material-notebook: Open `08_teleportation.ipynb`](https://github.com/TheQuantAI/quantsdk/blob/main/examples/08_teleportation.ipynb){ .md-button }

## What You'll Build

A **quantum teleportation** circuit — the protocol that transfers a quantum
state from one qubit to another using entanglement and classical bits.

## Background

Quantum teleportation doesn't move physical qubits — it transfers the
*quantum state* $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ from
Alice's qubit to Bob's qubit using:

1. A shared entangled (Bell) pair
2. A Bell measurement by Alice
3. Classical communication of 2 bits
4. Conditional corrections by Bob

## The Protocol

```
Alice has:  |psi> = alpha|0> + beta|1>  (qubit 0)
Shared:     Bell pair (qubits 1, 2)
Bob gets:   |psi> on qubit 2
```

## Step 1: Setup

```python
import quantsdk as qs
import math

# 3 qubits: q0 = Alice's state, q1 = Alice's Bell half, q2 = Bob's Bell half
circuit = qs.Circuit(3, name="teleportation")
```

## Step 2: Prepare the State to Teleport

Let's teleport the state $|\psi\rangle = RX(\pi/4)|0\rangle$:

```python
circuit.rx(0, math.pi / 4)  # Prepare |psi> on qubit 0
```

## Step 3: Create Shared Bell Pair

```python
circuit.barrier()  # Visual separator
circuit.h(1).cx(1, 2)  # Bell pair on qubits 1-2
```

## Step 4: Bell Measurement (Alice)

Alice entangles her state qubit with her Bell half, then measures:

```python
circuit.barrier()
circuit.cx(0, 1)  # CNOT: q0 -> q1
circuit.h(0)       # Hadamard on q0
circuit.measure(0)  # Measure q0
circuit.measure(1)  # Measure q1
```

## Step 5: Run the Circuit

```python
circuit.measure(2)  # Measure Bob's qubit too

result = qs.run(circuit, shots=1000)
print(result.counts)
```

!!! note
    In a real implementation, Bob would apply X and Z corrections based on
    Alice's measurement results. QuantSDK doesn't yet support classical
    conditionals (coming in v0.2), so we measure all qubits to verify
    the correlations statistically.

## Complete Code

```python
import quantsdk as qs
import math

# Create teleportation circuit
circuit = qs.Circuit(3, name="teleportation")

# Step 1: Prepare state to teleport
circuit.rx(0, math.pi / 4)

# Step 2: Create Bell pair (qubits 1-2)
circuit.barrier()
circuit.h(1).cx(1, 2)

# Step 3: Bell measurement (Alice)
circuit.barrier()
circuit.cx(0, 1).h(0)
circuit.measure(0).measure(1)

# Step 4: Measure Bob's qubit
circuit.measure(2)

# Run
result = qs.run(circuit, shots=4096)
print(result.counts)
print(result.summary())
```

## Understanding the Results

The measurement outcomes have 3 bits: `q0 q1 q2`.

- Bits `q0q1` are Alice's measurement results (random)
- Bit `q2` is Bob's qubit (correlated with Alice's results)

The protocol works because for each Alice outcome, Bob's qubit is in a
known rotation of $|\psi\rangle$.

## Key Takeaways

1. Teleportation transfers *quantum information*, not physical matter
2. It requires **entanglement** (shared Bell pair) + **classical communication** (2 bits)
3. It doesn't violate the no-cloning theorem — Alice's state is destroyed
4. It's the basis of **quantum networking** and **quantum error correction**

## Next Tutorial

:material-arrow-right: [Deutsch-Jozsa Algorithm](03-deutsch-jozsa.md) — your first quantum speedup.
