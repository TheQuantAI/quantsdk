# QuantSDK — Write Quantum Code Once, Run Anywhere

<p align="center">
  <strong>A framework-agnostic quantum computing SDK by <a href="https://thequantai.in">TheQuantAI</a></strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/quantsdk/"><img src="https://img.shields.io/pypi/v/quantsdk?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/quantsdk/"><img src="https://img.shields.io/pypi/pyversions/quantsdk" alt="Python versions"></a>
  <a href="https://github.com/TheQuantAI/quantsdk/blob/main/LICENSE"><img src="https://img.shields.io/github/license/TheQuantAI/quantsdk" alt="License"></a>
  <a href="https://github.com/TheQuantAI/quantsdk/actions"><img src="https://img.shields.io/github/actions/workflow/status/TheQuantAI/quantsdk/ci.yml?branch=main" alt="CI"></a>
</p>

---

## 🚀 What is QuantSDK?

QuantSDK is a **framework-agnostic** quantum computing SDK that lets you write quantum circuits once and run them on **any backend** — IBM Quantum, IonQ, Rigetti, D-Wave, GPU simulators, and more.

No more vendor lock-in. No more rewriting circuits for each framework. **One API, every quantum computer.**

## ✨ Features

- 🔌 **Framework-Agnostic** — Write once, export to Qiskit, Cirq, PennyLane, or OpenQASM
- ⚡ **Smart Routing** — QuantRouter automatically picks the best backend for your circuit
- 🧱 **Pythonic API** — Clean, intuitive, minimal boilerplate
- 🎯 **50+ Gates** — Full gate library including parametric and multi-qubit gates
- 📊 **Rich Results** — Histograms, probabilities, DataFrames, Bloch sphere
- 🔄 **Interop** — Seamless import/export with Qiskit, Cirq, PennyLane circuits
- 🆓 **Open Source** — Apache 2.0 license

## 📦 Installation

```bash
pip install quantsdk
```

With optional backends:
```bash
pip install quantsdk[ibm]     # IBM Quantum support
pip install quantsdk[gpu]     # GPU simulator support
pip install quantsdk[interop] # Qiskit/Cirq/PennyLane interop
pip install quantsdk[all]     # Everything
```

## 🏁 Quick Start

```python
import quantsdk as qs

# Create a Bell State circuit
circuit = qs.Circuit(2, name="bell_state")
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

# Run on local simulator (default)
result = qs.run(circuit, shots=1000)

print(result.counts)         # {'00': 503, '11': 497}
print(result.probabilities)  # {'00': 0.503, '11': 0.497}
print(result.most_likely)    # '00'

# Export to any framework
qiskit_circuit = circuit.to_qiskit()
cirq_circuit = circuit.to_cirq()
```

## 🔌 Run on Real Quantum Hardware

```python
# Run on IBM Quantum
result = qs.run(circuit, backend="ibm_brisbane", shots=1000)

# Smart routing — let QuantRouter pick the best backend
result = qs.run(circuit,
    optimize_for="quality",
    max_cost_usd=0.50,
    shots=1000)
```

## 📖 Documentation

- [Getting Started](https://docs.thequantcloud.com/getting-started/)
- [API Reference](https://docs.thequantcloud.com/api/)
- [Tutorials](https://docs.thequantcloud.com/tutorials/)
- [Backend Guides](https://docs.thequantcloud.com/backends/)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

Apache 2.0 — see [LICENSE](LICENSE) for details.

## 🏢 About TheQuantAI

QuantSDK is built by [TheQuantAI](https://thequantai.in) — building the infrastructure layer for quantum computing. Part of [TheQuantCloud](https://thequantcloud.com) platform.
