"""
Reversible projection coordinate maps (Phi / Phi^-1).
Handles the translation from bounded state intervals to unconstrained linear spaces.
"""
import numpy as np
from .math_utils import lambert_w0


class BaseBoundaryMap:
    """Abstract interface defining the requirements for variable coordinate transforms."""
    def forward(self, x: float) -> float:
        raise NotImplementedError
        
    def inverse(self, g: float) -> float:
        raise NotImplementedError


class RatioBoundaryMap(BaseBoundaryMap):
    """Maps dynamic variables defined on (0, x_max] to unconstrained space (0, inf)."""
    def __init__(self, x_max: float):
        self.x_max = x_max

    def forward(self, x: float) -> float:
        x_safe = np.clip(x, 1e-6, self.x_max - 1e-6)
        return x_safe / (self.x_max - x_safe)

    def inverse(self, g: float) -> float:
        g_safe = np.maximum(g, 1e-9)
        return self.x_max * g_safe / (1.0 + g_safe)


class SaturatingExponentialBoundaryMap(BaseBoundaryMap):
    """Maps saturating variables defined on [0, x_max] to G-space based on Michaelis-Menten mechanics."""
    def __init__(self, k_m: float, x_max: float):
        self.k_m = k_m
        self.x_max = x_max

    def forward(self, x: float) -> float:
        x_safe = np.clip(x, 0.0, self.x_max)
        return x_safe * np.exp(x_safe / self.k_m)

    def inverse(self, g: float) -> float:
        val = lambert_w0(max(g, 0.0) / self.k_m)
        return np.clip(self.k_m * val, 0.0, self.x_max)