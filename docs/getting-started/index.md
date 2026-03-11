# Getting Started

Welcome to QuantSDK! This guide will get you up and running with quantum computing
in under 10 minutes.

## What is QuantSDK?

QuantSDK is a **framework-agnostic** quantum computing SDK that lets you write
quantum circuits once and run them on any backend — local simulators, IBM Quantum,
IonQ, or GPU-accelerated devices.

```python
import quantsdk as qs

circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
result = qs.run(circuit, shots=1000)
print(result.counts)  # {'00': 498, '11': 502}
```

## Quick Navigation

<div class="grid cards" markdown>

- :material-download:{ .lg .middle } **[Installation](installation.md)**

    Install QuantSDK and optional backends in one command.

- :material-lightning-bolt:{ .lg .middle } **[Quickstart](quickstart.md)**

    Build and run your first quantum circuit in 5 minutes.

- :material-atom:{ .lg .middle } **[First Circuit](first-circuit.md)**

    Deep dive into building circuits with the fluent API.

- :material-server:{ .lg .middle } **[Real Hardware](real-hardware.md)**

    Run circuits on IBM Quantum and other real QPUs.

</div>

## Prerequisites

- **Python 3.10+** (3.12 recommended)
- Basic familiarity with Python
- No quantum computing knowledge required!

## Learning Path

| Step | Guide | Time |
|------|-------|------|
| 1 | [Installation](installation.md) | 2 min |
| 2 | [Quickstart](quickstart.md) | 5 min |
| 3 | [First Circuit](first-circuit.md) | 10 min |
| 4 | [Real Hardware](real-hardware.md) | 10 min |
| 5 | [Tutorials](../tutorials/index.md) | 30+ min |
