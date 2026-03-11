# API Reference

Complete reference documentation for all QuantSDK public APIs.

All classes and functions are auto-documented from source code docstrings.

## Core Modules

| Module | Description |
|--------|-------------|
| [`quantsdk.circuit`](circuit.md) | The `Circuit` class — core abstraction for building quantum circuits |
| [`quantsdk.gates`](gates.md) | All 50+ quantum gate classes with unitary matrix definitions |
| [`quantsdk.result`](result.md) | The `Result` class — measurement results, probabilities, and visualization |
| [`quantsdk.runner`](../api/index.md#quantsdkrun) | The `qs.run()` function — top-level circuit execution |
| [`quantsdk.backend`](backend.md) | `Backend` ABC, `BackendInfo`, and `BackendStatus` |

## Interop & Backends

| Module | Description |
|--------|-------------|
| [`quantsdk.interop`](interop.md) | Framework interop (Qiskit, OpenQASM, Cirq, PennyLane) |
| [`quantsdk.backends.ibm`](backend.md#ibm-backends) | IBM Quantum and Aer backend adapters |
| [`quantsdk.simulators.local`](backend.md#local-simulator) | Built-in pure-NumPy local simulator |

## Top-Level API

The most common entry points, available directly from `import quantsdk as qs`:

```python
import quantsdk as qs

qs.Circuit      # Build quantum circuits
qs.Result       # Inspect execution results
qs.run          # Execute circuits on any backend
qs.__version__  # SDK version string
```

### `quantsdk.run`

::: quantsdk.runner.run
    options:
      show_root_heading: true
      show_source: false
