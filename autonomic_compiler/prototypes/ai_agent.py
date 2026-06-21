"""
Prototype 2: Virtual AI Agent (Taskbacklog & Mental energy).
"""
import numpy as np
from autonomic_compiler.core import AutonomicCompiler
from autonomic_compiler.prototypes.base import BasePrototype


class VirtualAIAgentPrototype(BasePrototype):
    """
    Virtual Task-processing Assistant conforming to the BasePrototype contract.
    """
    def __init__(self):
        self.compiler = AutonomicCompiler()
        self.compiler.register_variable("cognitive_atp", 9.0, "ratio", max_limit=10.0)
        self.compiler.register_variable("knowledge_graph_coherence", 0.95, "ratio", max_limit=1.0)
        self.compiler.register_variable("message_buffer", 4.0, "saturating_exp", max_limit=100.0, k_m=20.0)

    def step(self, dt: float, **kwargs) -> None:
        incoming_messages = kwargs.get("incoming_messages", 2)
        
        cog_atp = self.compiler.get_value("cognitive_atp")
        coherence = self.compiler.get_value("knowledge_graph_coherence")
        buffer = self.compiler.get_value("message_buffer")
        
        processing_power = cog_atp / 10.0
        messages_processed = min(buffer, 12.0 * processing_power * dt)
        
        rates = {
            "cognitive_atp": -0.08 * (processing_power + 1.0),
            "knowledge_graph_coherence": 0.01 * coherence,
            "message_buffer": -0.05
        }
        
        forcings = {
            "cognitive_atp": -0.04 * messages_processed,
            "knowledge_graph_coherence": -0.015 * (buffer / 100.0) if buffer > 15.0 else 0.005,
            "message_buffer": float(incoming_messages) - messages_processed
        }
        
        self.compiler.compile_step(rates, forcings, dt)

    def get_diagnostics(self) -> dict:
        return {
            "cognitive_atp": self.compiler.get_value("cognitive_atp"),
            "knowledge_graph_coherence": self.compiler.get_value("knowledge_graph_coherence"),
            "message_buffer": self.compiler.get_value("message_buffer")
        }