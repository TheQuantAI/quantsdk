# TheQuantCloud — Getting Started

Welcome to **TheQuantCloud** — a cloud platform for running quantum circuits on simulators and real quantum hardware. This guide walks you through setup in under 5 minutes.

## What You Get (Free Tier)

| Feature | Limit |
|---------|-------|
| Simulator execution | 60 min/month |
| QPU tasks | 10/month |
| Credits | $50 (beta) |
| Saved circuits | Unlimited |
| API keys | 5 |

## Step 1: Create an Account

1. Go to [studio.thequantcloud.com/signup](https://studio.thequantcloud.com/signup)
2. Sign up with email or GitHub
3. Check your email for the confirmation link
4. Click the link to activate your account

## Step 2: Generate an API Key

1. Sign in to [QuantStudio](https://studio.thequantcloud.com/login)
2. Go to the [Connect page](https://studio.thequantcloud.com/connect) or [Dashboard](https://studio.thequantcloud.com/dashboard)
3. Click **Generate Key**, give it a name
4. Copy the key — it's only shown once!

!!! warning "Save Your Key"
    The API key is displayed **once**. Copy it immediately and store it securely. If you lose it, revoke and create a new one.

## Step 3: Install QuantSDK

```bash
pip install thequantsdk
```

## Step 4: Set Your API Key

=== "Environment Variable (recommended)"
    ```bash
    export QUANTCLOUD_API_KEY="qc_your_key_here"
    ```

=== "In Code"
    ```python
    import quantsdk as qs
    qs.configure(api_key="qc_your_key_here")
    ```

=== "Credentials File"
    ```bash
    mkdir -p ~/.quantcloud
    echo '{"api_key": "qc_your_key_here"}' > ~/.quantcloud/credentials.json
    ```

## Step 5: Run Your First Cloud Circuit

```python
import quantsdk as qs

# Create a Bell State circuit
circuit = qs.Circuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

# Run on the cloud (Qiskit Aer simulator)
result = qs.run(circuit, backend="aer_simulator", shots=1024)

# View results
print(result.counts)       # {'00': 512, '11': 512}
print(result.probabilities) # {'00': 0.5, '11': 0.5}
print(result.backend)       # 'aer_simulator'
```

## Step 6: Use QuantStudio Web IDE

Prefer a visual experience? Use [QuantStudio](https://studio.thequantcloud.com/studio) — our web-based quantum IDE with:

- **Monaco Code Editor** — syntax highlighting, autocomplete
- **One-Click Execution** — run on any backend from the dropdown
- **Live Visualizations** — histograms, probability bars, circuit diagrams
- **Built-in Terminal** — Pyodide Python terminal in the browser
- **Save & Load** — persist circuits to the cloud

## Available Backends

| Backend | Engine | Max Qubits | Cost |
|---------|--------|------------|------|
| `local_simulator` | QuantSDK NumPy | 20 | Free |
| `aer_simulator` | Qiskit Aer | 25 | Free (beta) |
| `aer_gpu_simulator` | Qiskit Aer + GPU | 30 | Free (beta) |
| `cirq_simulator` | Cirq DensityMatrix | 20 | Free (beta) |
| `pennylane_simulator` | PennyLane default | 20 | Free (beta) |

Real QPU backends (IBM, IonQ) will be added in future releases.

## API Base URL

All API requests go to:

```
https://api.thequantcloud.com/v1
```

## What's Next?

- [Cloud API Reference](../api/cloud-api.md) — full endpoint documentation
- [Tutorials](../tutorials/index.md) — step-by-step quantum algorithm tutorials
- [Examples](../examples/index.md) — 22 Jupyter notebooks

## Need Help?

- [GitHub Issues](https://github.com/TheQuantAI/quantsdk/issues) — bug reports and feature requests
- [Discord](https://discord.gg/quantsdk) — community chat
- Email: saket@thequantai.in
