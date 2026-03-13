# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Built-in quantum simulators for QuantSDK."""

from quantsdk.simulators.local import LocalSimulator

__all__ = ["GPUSimulator", "LocalSimulator"]


def __getattr__(name: str) -> object:
    if name == "GPUSimulator":
        from quantsdk.simulators.gpu import GPUSimulator

        return GPUSimulator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
