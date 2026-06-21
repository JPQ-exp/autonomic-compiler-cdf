"""
Prototype 1: Autonomous Mobile Robot (Control & Power Management).
"""
import numpy as np
from autonomic_compiler.core import AutonomicCompiler
from autonomic_compiler.prototypes.base import BasePrototype


class AutonomousRobotPrototype(BasePrototype):
    """
    Industrial mobile robot simulator conforming to the BasePrototype contract.
    """
    def __init__(self):
        self.compiler = AutonomicCompiler()
        self.compiler.register_variable("battery", 22.0, "ratio", max_limit=24.0)
        self.compiler.register_variable("structural_integrity", 98.0, "ratio", max_limit=100.0)
        self.compiler.register_variable("capacitor", 12.0, "saturating_exp", max_limit=50.0, k_m=10.0)
        
        self.position = np.array([0.0, 0.0])
        self.target = np.array([8.0, 8.0])
        self.charging_pad = np.array([1.0, 1.0])

    def step(self, dt: float, **kwargs) -> None:
        dist_to_target = np.linalg.norm(self.target - self.position)
        dist_to_charger = np.linalg.norm(self.charging_pad - self.position)
        
        battery = self.compiler.get_value("battery")
        capacitor = self.compiler.get_value("capacitor")
        
        need_recharge = battery < 8.0
        active_target = self.charging_pad if need_recharge else self.target
        active_dist = dist_to_charger if need_recharge else dist_to_target

        if active_dist > 0.2:
            direction = (active_target - self.position) / active_dist
            speed = 2.0 * (battery / 24.0)
            velocity = direction * speed
        else:
            velocity = np.array([0.0, 0.0])

        is_charging = need_recharge and (dist_to_charger <= 0.2)
        if is_charging:
            velocity = np.array([0.0, 0.0])
            self.position = self.charging_pad.copy()
        else:
            self.position += velocity * dt

        kinetic_cost = float(np.dot(velocity, velocity))
        
        rates = {
            "battery": -0.01 * (1.0 + kinetic_cost),
            "structural_integrity": -0.005,
            "capacitor": -0.04
        }
        
        forcings = {
            "battery": 5.0 if is_charging else -0.05,
            "structural_integrity": 0.01 * (capacitor / 50.0),
            "capacitor": 10.0 if is_charging else -0.02 * kinetic_cost
        }
        
        self.compiler.compile_step(rates, forcings, dt)

    def get_diagnostics(self) -> dict:
        return {
            "x_pos": float(self.position[0]),
            "y_pos": float(self.position[1]),
            "battery": self.compiler.get_value("battery"),
            "structural_integrity": self.compiler.get_value("structural_integrity"),
            "capacitor": self.compiler.get_value("capacitor")
        }