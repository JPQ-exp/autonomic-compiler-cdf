"""
The primary Autonomic Compilation Runtime.
Manages state dynamic registration and safe transformation integration passes.
"""
import numpy as np
from typing import Dict, Any
from .boundary_maps import RatioBoundaryMap, SaturatingExponentialBoundaryMap
from .math_utils import exact_linear_step


class AutonomicCompiler:
    """
    State dynamic compiler.
    Transforms arbitrary parameters into G-space, integrates exactly, and maps back.
    """
    def __init__(self):
        self.variables: Dict[str, Dict[str, Any]] = {}

    def register_variable(self, name: str, initial_value: float, map_type: str, max_limit: float, **kwargs):
        """Registers a dynamic parameter schema with strict safety map envelopes."""
        if map_type == "ratio":
            b_map = RatioBoundaryMap(max_limit)
        elif map_type == "saturating_exp":
            k_m = kwargs.get("k_m", 50.0)
            b_map = SaturatingExponentialBoundaryMap(k_m, max_limit)
        else:
            raise ValueError(f"Mapping transformation type '{map_type}' is unsupported.")

        self.variables[name] = {
            "value": initial_value,
            "map": b_map,
            "max": max_limit,
            "meta": kwargs
        }

    def get_value(self, name: str) -> float:
        return self.variables[name]["value"]

    def set_value(self, name: str, val: float):
        self.variables[name]["value"] = val

    def compile_step(self, rates: Dict[str, float], forcings: Dict[str, float], dt: float):
        """
        Executes a dynamic step pass over all registered variables.
        Maps values to unconstrained space, applies exact integration, and pulls back safely.
        """
        for name, var_config in self.variables.items():
            current_val = var_config["value"]
            b_map = var_config["map"]
            
            # Map into unconstrained coordinates (Phi)
            g_0 = b_map.forward(current_val)
            
            # Extract dynamics configuration
            rate = rates.get(name, 0.0)
            forcing = forcings.get(name, 0.0)
            
            # Apply integration kernel
            g_next = exact_linear_step(g_0, rate, forcing, dt)
            
            # Return safely to bounded coordinate plane (Phi^-1)
            val_next = b_map.inverse(g_next)
            
            # Final backstop clamping to protect against floating point rounding edge-cases
            val_next = np.clip(val_next, 1e-4, var_config["max"] * (1.0 - 1e-8))
            var_config["value"] = float(val_next)