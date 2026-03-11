# Installation

## Quick Install

```bash
pip install quantsdk
```

This installs the core SDK with the local simulator. No external dependencies
beyond NumPy are required.

## Optional Dependencies

QuantSDK uses optional dependency groups so you only install what you need:

=== "IBM Quantum"
    ```bash
    pip install quantsdk[ibm]
    ```
    Includes `qiskit`, `qiskit-ibm-runtime`, and `qiskit-aer` for IBM backends.

=== "Qiskit Interop"
    ```bash
    pip install quantsdk[interop]
    ```
    Includes `qiskit` for circuit conversion and OpenQASM export.

=== "Visualization"
    ```bash
    pip install quantsdk[viz]
    ```
    Includes `matplotlib` and `pandas` for histograms and DataFrames.

=== "GPU Simulator"
    ```bash
    pip install quantsdk[gpu]
    ```
    Includes `cuquantum` for GPU-accelerated simulation (requires NVIDIA GPU).

=== "Everything"
    ```bash
    pip install quantsdk[all]
    ```
    Installs all optional dependencies.

## Development Install

For contributing or development:

```bash
git clone https://github.com/TheQuantAI/quantsdk.git
cd quantsdk
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,docs]"
```

## Verify Installation

```python
import quantsdk as qs
print(qs.__version__)  # 0.1.0-dev

# Quick smoke test
circuit = qs.Circuit(1).h(0).measure_all()
result = qs.run(circuit, shots=100)
print(result.counts)  # {'0': ~50, '1': ~50}
```

## Python Version Support

| Python Version | Status |
|---------------|--------|
| 3.10 | :material-check-circle:{ style="color: green" } Supported |
| 3.11 | :material-check-circle:{ style="color: green" } Supported |
| 3.12 | :material-check-circle:{ style="color: green" } Recommended |
| 3.13 | :material-check-circle:{ style="color: green" } Supported |
| < 3.10 | :material-close-circle:{ style="color: red" } Not supported |

## Troubleshooting

### ImportError: No module named 'quantsdk'

Make sure you have activated the correct virtual environment:

```bash
which python  # Should point to your venv
pip list | grep quantsdk
```

### Qiskit import errors

If you see errors about Qiskit, install the interop extras:

```bash
pip install quantsdk[interop]
```

### IBM Backend authentication

For IBM Quantum access, you need an API token:

```python
from quantsdk.backends.ibm import IBMBackend
backend = IBMBackend(token="your-ibm-token")
```

Get your token at [quantum.ibm.com](https://quantum.ibm.com).
