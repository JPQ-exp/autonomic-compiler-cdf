"""
Decision selection and lateral inhibition gating mechanics.
"""
import numpy as np


def competitive_gate(w: np.ndarray, reactive_mask: np.ndarray = None) -> np.ndarray:
    """
    Lateral-inhibition gate to resolve command conflicts.
    Reactive behaviors bypass mutual inhibition to act as emergency overrides.
    """
    psi_t = 1.0 / (1.0 + np.exp(-2.0 * w))
    if reactive_mask is None:
        reactive_mask = np.zeros_like(w, dtype=bool)
    
    pool_total = psi_t[~reactive_mask].sum() if np.any(~reactive_mask) else 0.0
    psi = np.empty_like(w, dtype=float)
    for i in range(len(w)):
        if reactive_mask[i]:
            # Direct non-inhibited activation path
            psi[i] = np.maximum(psi_t[i], 0.0) + np.log1p(np.exp(-np.abs(psi_t[i])))
        else:
            # Inhibited by competitive neighbors
            inhibition = pool_total - psi_t[i]
            val = psi_t[i] - inhibition
            psi[i] = np.maximum(val, 0.0) + np.log1p(np.exp(-np.abs(val)))
    return psi