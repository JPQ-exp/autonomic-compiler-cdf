"""
Abstract base class contract definition for autonomic prototypes.
Acts as a leaf node in the import graph to prevent package-level circular loops.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BasePrototype(ABC):
    """
    Unified programming contract for all autonomic prototypes.
    Enforces a standardized execution and telemetry acquisition loop.
    """
    
    @abstractmethod
    def step(self, dt: float, **kwargs) -> None:
        """Advance the prototype state by dt using optional environment inputs."""
        pass

    @abstractmethod
    def get_diagnostics(self) -> Dict[str, Any]:
        """Expose current compiled internal safety variables."""
        pass