# Backend

The backend system defines the contract that all quantum execution backends
must implement.

## Architecture

```
Backend (ABC)
├── LocalSimulator      — Pure NumPy, built-in, no dependencies
├── AerBackend          — Qiskit Aer, high-performance simulator
├── IBMBackend          — IBM Quantum real hardware
├── IonQBackend         — IonQ trapped-ion processors (v0.2)
└── CustomBackend       — Your own backend
```

## Core Interfaces

### Backend ABC

::: quantsdk.backend.Backend
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members_order: source

### BackendInfo

::: quantsdk.backend.BackendInfo
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4
      show_signature_annotations: true

### BackendStatus

::: quantsdk.backend.BackendStatus
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

---

## Local Simulator

The built-in simulator uses pure NumPy tensor contraction. No external
dependencies required.

::: quantsdk.simulators.local.LocalSimulator
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members_order: source
      filters:
        - "!^_"

### Usage

```python
import quantsdk as qs

# Via qs.run() (recommended)
result = qs.run(circuit, shots=1000)

# Or directly
from quantsdk.simulators.local import LocalSimulator

sim = LocalSimulator()
info = sim.info()
print(f"Max qubits: {info.num_qubits}")  # 24

result = sim.run(circuit, shots=1000, seed=42)
```

### Limitations

- Maximum 24 qubits (memory constraint)
- No noise modeling (use Aer for noise simulation)
- CPU only (use GPU backend for large circuits)

---

## IBM Backends

Requires `pip install quantsdk[ibm]`.

::: quantsdk.backends.ibm.IBMBackend
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members_order: source
      filters:
        - "!^_"

::: quantsdk.backends.ibm.AerBackend
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4
      show_signature_annotations: true
      members_order: source
      filters:
        - "!^_"
