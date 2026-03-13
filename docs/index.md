---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

# ⚛️ QuantSDK

### Write quantum code once, run anywhere.

A **framework-agnostic** quantum computing SDK by [TheQuantAI](https://thequantai.in).

[Get Started :material-rocket-launch:](getting-started/quickstart.md){ .md-button .md-button--primary }
[API Reference :material-book-open-variant:](api/index.md){ .md-button }

</div>

---

## Why QuantSDK?

| Problem | QuantSDK Solution |
|---------|------------------|
| **Vendor lock-in** — rewriting circuits for each framework | Write once in QuantSDK, export to Qiskit, Cirq, PennyLane, or OpenQASM |
| **Backend complexity** — each provider has different APIs | `qs.run(circuit, backend="ibm_brisbane")` — one line, any backend |
| **Steep learning curve** — quantum SDKs are verbose | Pythonic, fluent API with `circuit.h(0).cx(0, 1).measure_all()` |
| **No smart routing** — manually choosing optimal hardware | QuantRouter picks the best backend for your circuit (coming v0.2) |

---

## Quick Example

```python
import quantsdk as qs

# Create a Bell State
circuit = qs.Circuit(2, name="bell")
circuit.h(0).cx(0, 1).measure_all()

# Run locally (instant, free)
result = qs.run(circuit, shots=1000)
print(result.counts)        # {'00': 512, '11': 488}
print(result.most_likely)   # '00'

# Visualize
result.plot_histogram()

# Export to any framework
qc = circuit.to_qiskit()
qasm = circuit.to_openqasm()
```

---

## Feature Highlights

<div class="grid cards" markdown>

- :material-swap-horizontal:{ .lg .middle } **Framework Interop**

    ---

    Seamlessly convert to and from Qiskit, Cirq, PennyLane, and OpenQASM 2.0.

    [:octicons-arrow-right-24: Learn more](api/interop.md)

- :material-atom:{ .lg .middle } **50+ Quantum Gates**

    ---

    Full gate library: Pauli, Clifford, controlled, parametric rotations, multi-qubit, and more.

    [:octicons-arrow-right-24: Gate reference](api/gates.md)

- :material-chart-bar:{ .lg .middle } **Rich Results**

    ---

    Histograms, probabilities, DataFrames, expectation values — all built in.

    [:octicons-arrow-right-24: Result API](api/result.md)

- :material-server-network:{ .lg .middle } **Multiple Backends**

    ---

    Local simulator, IBM Quantum, IonQ, GPU — one API for all.

    [:octicons-arrow-right-24: Backend guides](backends/index.md)

</div>

---

## Installation

```bash
pip install thequantsdk
```

With optional backends:

=== "IBM Quantum"
    ```bash
    pip install thequantsdk[ibm]
    ```

=== "GPU Simulator"
    ```bash
    pip install thequantsdk[gpu]
    ```

=== "Everything"
    ```bash
    pip install thequantsdk[all]
    ```

---

## Project Status

| Component | Status | Version |
|-----------|--------|---------|
| Core SDK | :material-check-circle:{ style="color: green" } Stable | 0.1.0-dev |
| Gate Library | :material-check-circle:{ style="color: green" } 50+ gates | 0.1.0-dev |
| Local Simulator | :material-check-circle:{ style="color: green" } Working | 0.1.0-dev |
| Qiskit Interop | :material-check-circle:{ style="color: green" } Working | 0.1.0-dev |
| OpenQASM Interop | :material-check-circle:{ style="color: green" } Working | 0.1.0-dev |
| IBM Backend | :material-check-circle:{ style="color: green" } Working | 0.1.0-dev |
| Aer Backend | :material-check-circle:{ style="color: green" } Working | 0.1.0-dev |
| QuantRouter | :material-clock-outline:{ style="color: orange" } v0.2 | Planned |
| Cirq Interop | :material-clock-outline:{ style="color: orange" } v0.2 | Planned |
| PennyLane Interop | :material-clock-outline:{ style="color: orange" } v0.2 | Planned |

---

<div style="text-align: center; padding: 2rem 0;" markdown>

**Built with :material-heart: by [TheQuantAI](https://thequantai.in)** — Part of [TheQuantCloud](https://thequantcloud.com)

</div>
