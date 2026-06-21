"""
Prototype 3: Astro-cellular Organism (Metabolic triage).
"""
import numpy as np
from autonomic_compiler.core import AutonomicCompiler
from autonomic_compiler.prototypes.base import BasePrototype


class AstrobiologyOrganismPrototype(BasePrototype):
    """
    Simulated dynamic lifeform conforming to the BasePrototype contract.
    """
    def __init__(self):
        self.compiler = AutonomicCompiler()
        self.compiler.register_variable("glycogen", 50.0, "saturating_exp", max_limit=150.0, k_m=30.0)
        self.compiler.register_variable("biological_atp", 10.0, "ratio", max_limit=15.0)
        self.compiler.register_variable("somatic_mass", 75.0, "ratio", max_limit=100.0)

    def step(self, dt: float, **kwargs) -> None:
        food_available = kwargs.get("food_available", 0.0)
        toxic_radiation = kwargs.get("toxic_radiation", 0.0)
        
        glycogen = self.compiler.get_value("glycogen")
        atp = self.compiler.get_value("biological_atp")
        mass = self.compiler.get_value("somatic_mass")
        
        is_starving = glycogen < 12.0
        catabolic_recycling = 0.4 * mass * dt if is_starving else 0.0
        anabolic_growth = 0.08 * atp * (1.0 - mass / 100.0)
        
        rates = {
            "glycogen": -0.04,
            "biological_atp": -0.08 * (toxic_radiation + 1.0),
            "somatic_mass": -0.015 * (toxic_radiation + 1.0)
        }
        
        forcings = {
            "glycogen": 4.0 * food_available - (0.15 * anabolic_growth),
            "biological_atp": 1.2 * (glycogen / (glycogen + 6.0)) + 0.6 * catabolic_recycling - 0.25 * anabolic_growth,
            "somatic_mass": anabolic_growth - catabolic_recycling
        }
        
        self.compiler.compile_step(rates, forcings, dt)

    def get_diagnostics(self) -> dict:
        return {
            "glycogen": self.compiler.get_value("glycogen"),
            "biological_atp": self.compiler.get_value("biological_atp"),
            "somatic_mass": self.compiler.get_value("somatic_mass")
        }