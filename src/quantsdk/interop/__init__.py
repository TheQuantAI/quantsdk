# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Framework interop — convert between QuantSDK and other quantum frameworks."""

from quantsdk.interop.openqasm import from_openqasm, to_openqasm
from quantsdk.interop.qiskit_interop import from_qiskit, to_qiskit

__all__ = [
    "from_cirq",
    "from_openqasm",
    "from_pennylane",
    "from_qiskit",
    "to_cirq",
    "to_openqasm",
    "to_pennylane",
    "to_qiskit",
]


def __getattr__(name: str) -> object:
    if name in ("to_cirq", "from_cirq"):
        from quantsdk.interop.cirq_interop import from_cirq, to_cirq

        globals()["to_cirq"] = to_cirq
        globals()["from_cirq"] = from_cirq
        return to_cirq if name == "to_cirq" else from_cirq
    if name in ("to_pennylane", "from_pennylane"):
        from quantsdk.interop.pennylane_interop import from_pennylane, to_pennylane

        globals()["to_pennylane"] = to_pennylane
        globals()["from_pennylane"] = from_pennylane
        return to_pennylane if name == "to_pennylane" else from_pennylane
    raise AttributeError(f"module 'quantsdk.interop' has no attribute {name!r}")
