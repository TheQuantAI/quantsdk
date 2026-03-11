# Gates

QuantSDK provides 50+ quantum gate classes covering single-qubit, two-qubit,
three-qubit, and special operations.

## Gate Hierarchy

All gates inherit from the `Gate` base class:

```
Gate (base)
├── Single-Qubit Gates
│   ├── HGate, XGate, YGate, ZGate, IGate
│   ├── SGate, SdgGate, TGate, TdgGate
│   ├── SXGate, SXdgGate
│   ├── RXGate, RYGate, RZGate, RGate
│   ├── PhaseGate, U1Gate, U2Gate, U3Gate
│   └── Reset
├── Two-Qubit Gates
│   ├── CXGate, CYGate, CZGate, CHGate
│   ├── CSGate, CSdgGate, CSXGate
│   ├── CRXGate, CRYGate, CRZGate, CPhaseGate
│   ├── CU1Gate, CU3Gate
│   ├── SwapGate, iSwapGate, DCXGate, ECRGate
│   └── RZZGate, RXXGate, RYYGate, RZXGate
├── Three-Qubit Gates
│   ├── ToffoliGate (CCX)
│   ├── CCZGate
│   └── FredkinGate (CSWAP)
└── Special Operations
    ├── Measure
    └── Barrier
```

## Quick Reference Table

| Gate | Class | Qubits | Parameters | Description |
|------|-------|--------|------------|-------------|
| H | `HGate` | 1 | — | Hadamard |
| X | `XGate` | 1 | — | Pauli-X (NOT) |
| Y | `YGate` | 1 | — | Pauli-Y |
| Z | `ZGate` | 1 | — | Pauli-Z |
| I | `IGate` | 1 | — | Identity |
| S | `SGate` | 1 | — | $\pi/2$ phase |
| Sdg | `SdgGate` | 1 | — | S-dagger |
| T | `TGate` | 1 | — | $\pi/4$ phase |
| Tdg | `TdgGate` | 1 | — | T-dagger |
| SX | `SXGate` | 1 | — | $\sqrt{X}$ |
| SXdg | `SXdgGate` | 1 | — | $\sqrt{X}$-dagger |
| RX | `RXGate` | 1 | $\theta$ | X-rotation |
| RY | `RYGate` | 1 | $\theta$ | Y-rotation |
| RZ | `RZGate` | 1 | $\theta$ | Z-rotation |
| R | `RGate` | 1 | $\theta, \phi$ | General rotation |
| Phase | `PhaseGate` | 1 | $\lambda$ | Phase gate |
| U1 | `U1Gate` | 1 | $\lambda$ | U1 ($= \text{Phase}$) |
| U2 | `U2Gate` | 1 | $\phi, \lambda$ | U2 |
| U3 | `U3Gate` | 1 | $\theta, \phi, \lambda$ | General unitary |
| CX | `CXGate` | 2 | — | CNOT |
| CY | `CYGate` | 2 | — | Controlled-Y |
| CZ | `CZGate` | 2 | — | Controlled-Z |
| CH | `CHGate` | 2 | — | Controlled-H |
| CS | `CSGate` | 2 | — | Controlled-S |
| CSdg | `CSdgGate` | 2 | — | Controlled-Sdg |
| CSX | `CSXGate` | 2 | — | Controlled-SX |
| CRX | `CRXGate` | 2 | $\theta$ | Controlled-RX |
| CRY | `CRYGate` | 2 | $\theta$ | Controlled-RY |
| CRZ | `CRZGate` | 2 | $\theta$ | Controlled-RZ |
| CP | `CPhaseGate` | 2 | $\lambda$ | Controlled-Phase |
| CU1 | `CU1Gate` | 2 | $\lambda$ | Controlled-U1 |
| CU3 | `CU3Gate` | 2 | $\theta, \phi, \lambda$ | Controlled-U3 |
| SWAP | `SwapGate` | 2 | — | SWAP |
| iSWAP | `iSwapGate` | 2 | — | iSWAP |
| DCX | `DCXGate` | 2 | — | Double-CX |
| ECR | `ECRGate` | 2 | — | Echoed CR |
| RZZ | `RZZGate` | 2 | $\theta$ | ZZ-interaction |
| RXX | `RXXGate` | 2 | $\theta$ | XX-interaction |
| RYY | `RYYGate` | 2 | $\theta$ | YY-interaction |
| RZX | `RZXGate` | 2 | $\theta$ | ZX-interaction |
| CCX | `ToffoliGate` | 3 | — | Toffoli |
| CCZ | `CCZGate` | 3 | — | Controlled-CZ |
| CSWAP | `FredkinGate` | 3 | — | Fredkin |

## API Reference

### Base Class

::: quantsdk.gates.Gate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### Single-Qubit Gates

::: quantsdk.gates.HGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.XGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.YGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.ZGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.IGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.SGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.SdgGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.TGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.TdgGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.SXGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.SXdgGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.RXGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.RYGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.RZGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.RGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.PhaseGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.U1Gate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.U2Gate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.U3Gate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### Two-Qubit Gates

::: quantsdk.gates.CXGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CYGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CZGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CHGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CSGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CSdgGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CSXGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CRXGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CRYGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CRZGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CPhaseGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CU1Gate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CU3Gate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.SwapGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.iSwapGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.DCXGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.ECRGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.RZZGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.RXXGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.RYYGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.RZXGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### Three-Qubit Gates

::: quantsdk.gates.ToffoliGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.CCZGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.FredkinGate
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### Special Operations

::: quantsdk.gates.Measure
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.Barrier
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

::: quantsdk.gates.Reset
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### Gate Map

The `GATE_MAP` dictionary maps string names to gate classes for
use in deserialization and interop:

```python
from quantsdk.gates import GATE_MAP

# 55 entries mapping string names -> Gate classes
print(list(GATE_MAP.keys()))
# ['h', 'x', 'y', 'z', 'i', 'id', 's', 'sdg', 't', 'tdg', ...]
```
