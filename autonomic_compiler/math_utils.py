"""
Numerical kernels, transcendental functions, and analytical ODE solvers.
Provides overflow protections and safe bounds for floating-point calculations.
"""
import numpy as np


def safe_exp(x: float) -> float:
    """Clamped exponential to prevent floating-point overflows."""
    return float(np.exp(np.clip(x, -50.0, 50.0)))


def lambert_w0(z: float, iters: int = 15) -> float:
    """
    Principal branch of the Lambert W function, z >= 0, solved via Halley's method.
    Provides dependency-free transcendental inversion for exponential state paths.
    """
    if z <= 0.0:
        return 0.0
    if z > 1.0:
        w = np.log(z) - np.log(np.log(z))
    else:
        w = z * (1.0 - z + 1.5 * z * z)
    
    for _ in range(iters):
        ew = safe_exp(w)
        f = w * ew - z
        # Halley's method adjustment step
        w -= f / (ew * (w + 1.0) - (w + 2.0) * f / (2.0 * w + 2.0))
    return w


def exact_linear_step(g: float, rate: float, forcing: float, dt: float) -> float:
    """
    Solves dg/dt = rate * g + forcing analytically over interval dt.
    Keeps rate and forcing frozen at start-of-tick values to remove discretization errors.
    """
    if abs(rate) < 1e-9:
        return g + forcing * dt
    factor = safe_exp(rate * dt)
    return g * factor + forcing * (factor - 1.0) / rate