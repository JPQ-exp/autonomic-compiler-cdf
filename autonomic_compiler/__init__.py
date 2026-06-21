"""
Autonomic Limits Compiler core package initialization.
"""
from .core import AutonomicCompiler
from .gates import competitive_gate

__all__ = ["AutonomicCompiler", "competitive_gate"]