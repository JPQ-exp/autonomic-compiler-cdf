"""
main.py
Interactive CLI for selecting, parameterizing, and running autonomic prototypes.
Dynamically tracks state history and generates 3-panel safety limit plots.
"""

import os
import sys

# Ensure parent root is dynamically injected to resolve 'autonomic_compiler' imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Expose the direct interface contract
from autonomic_compiler.prototypes.base import BasePrototype


def print_telemetry_line(step: int, inputs: dict, metrics: dict):
    """Outputs a single, clean formatted line of telemetry."""
    input_str = " | ".join([f"{k}: {v: >4}" for k, v in inputs.items()]) or "No external inputs"
    metrics_str = " | ".join([f"{k}: {v: >6.2f}" for k, v in metrics.items()])
    print(f"  Step {step:03d} -> [Inputs] {input_str:<40} || [States] {metrics_str}")


def get_user_parameters() -> tuple:
    """Prompt the user for simulation parameters with robust fallback defaults."""
    steps_in = input("Enter simulation steps (default: 100): ").strip()
    try:
        steps = int(steps_in) if steps_in else 100
    except ValueError:
        print("[Warn] Invalid input. Defaulting to 100 steps.")
        steps = 100

    dt_in = input("Enter timestep dt (default: 0.1): ").strip()
    try:
        dt = float(dt_in) if dt_in else 0.1
    except ValueError:
        print("[Warn] Invalid input. Defaulting to dt=0.1.")
        dt = 0.1

    return steps, dt


def plot_simulation_results(title: str, time_history: list, history: dict, limits: dict):
    """
    Renders a clean 3-panel safety plot.
    Degrades gracefully if matplotlib is uninstalled or if run in headless systems.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n" + "-"*85)
        print("[Notice] matplotlib is not installed. Visual plotting bypassed.")
        print("To enable visual plotting, please run: pip install matplotlib")
        print("-" * 85)
        return

    # Initialize a 1-row, 3-column layout (one subplot per registered variable)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharex=True)
    fig.suptitle(f"Autonomic Safety Analysis: {title}", fontsize=13, fontweight='bold', y=0.98)

    for ax, (var_name, values) in zip(axes, history.items()):
        # Plot continuous state trajectory
        ax.plot(time_history, values, label='State Curve', color='#1f77b4', linewidth=2)
        
        # Draw asymptotic threshold boundary if limit parameter exists
        if var_name in limits:
            limit_val = limits[var_name]
            ax.axhline(limit_val, color='#d62728', linestyle='--', linewidth=1.5,
                       label=f'Safety Boundary ({limit_val})')
            
        # Format subplot aesthetic details
        title_clean = var_name.replace('_', ' ').title()
        ax.set_title(title_clean, fontsize=10, fontweight='semibold', pad=8)
        ax.set_xlabel('Time (seconds)', fontsize=8)
        ax.set_ylabel('Simulated Value', fontsize=8)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.tick_params(labelsize=8)
        ax.legend(loc='best', fontsize=8)

    plt.tight_layout()

    # Headless-safe save utility
    filename = f"plot_{title.lower().replace(' ', '_').replace(':', '')}.png"
    try:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n[Visualizer] Trajectory plot safely saved to directory: '{filename}'")
    except Exception as e:
        print(f"\n[Visualizer] Could not write plot image to disk: {e}")

    # Headless-safe interactive display
    try:
        plt.show()
    except Exception:
        print("[Visualizer] Headless runtime context detected. Interactive UI window bypassed.")


def run_robot_simulation():
    """Loads and executes the AMR Robot using BasePrototype interface bindings."""
    steps, dt = get_user_parameters()
    
    # Direct absolute file lookup, bypassing __init__.py package side-effects
    from autonomic_compiler.prototypes.amr_robot import AutonomousRobotPrototype
    
    # Enforces interface contract compliance
    agent: BasePrototype = AutonomousRobotPrototype()
    
    print("\n" + "="*85)
    print(f" SIMULATING: Autonomous Mobile Robot (Steps: {steps}, dt: {dt})")
    print("="*85)
    
    # Track limits matching registrations inside amr_robot.py
    limits = {"battery": 24.0, "structural_integrity": 100.0, "capacitor": 50.0}
    
    # Initialize history tracking vectors
    time_history = [0.0]
    history = {k: [v] for k, v in agent.get_diagnostics().items() if k not in ("x_pos", "y_pos")}

    print_telemetry_line(0, {}, agent.get_diagnostics())
    print("-" * 85)

    for step in range(1, steps + 1):
        agent.step(dt)
        
        # Collect dynamic trajectory values at every frame step
        diagnostics = agent.get_diagnostics()
        time_history.append(step * dt)
        for k, v in diagnostics.items():
            if k in history:
                history[k].append(v)
        
        # Log to terminal console periodically
        if step % max(1, steps // 4) == 0 or step == steps:
            print_telemetry_line(step, {}, diagnostics)
            
    print("="*85)
    
    # Send history arrays to the visualizer
    plot_simulation_results("Autonomous Mobile Robot", time_history, history, limits)


def run_ai_simulation():
    """Loads and executes the AI Cognitive Agent with workloads."""
    steps, dt = get_user_parameters()
    
    from autonomic_compiler.prototypes.ai_agent import VirtualAIAgentPrototype
    agent: BasePrototype = VirtualAIAgentPrototype()
    
    print("\n" + "="*85)
    print(f" SIMULATING: Virtual AI Agent (Steps: {steps}, dt: {dt})")
    print("="*85)
    
    limits = {"cognitive_atp": 10.0, "knowledge_graph_coherence": 1.0, "message_buffer": 100.0}
    time_history = [0.0]
    history = {k: [v] for k, v in agent.get_diagnostics().items()}

    print_telemetry_line(0, {}, agent.get_diagnostics())
    print("-" * 85)

    for step in range(1, steps + 1):
        # Peak traffic load midway through execution
        message_rate = 25 if (0.3 * steps < step < 0.7 * steps) else 2
        inputs = {"incoming_messages": message_rate}
        
        agent.step(dt, **inputs)
        
        diagnostics = agent.get_diagnostics()
        time_history.append(step * dt)
        for k, v in diagnostics.items():
            if k in history:
                history[k].append(v)
        
        if step % max(1, steps // 4) == 0 or step == steps:
            print_telemetry_line(step, inputs, diagnostics)
            
    print("="*85)
    plot_simulation_results("Virtual AI Agent", time_history, history, limits)


def run_astrobiology_simulation():
    """Loads and executes the Astrobiological Cell under toxic environments."""
    steps, dt = get_user_parameters()
    
    from autonomic_compiler.prototypes.astrobiology import AstrobiologyOrganismPrototype
    agent: BasePrototype = AstrobiologyOrganismPrototype()
    
    print("\n" + "="*85)
    print(f" SIMULATING: Astrobiological Organism (Steps: {steps}, dt: {dt})")
    print("="*85)
    
    limits = {"glycogen": 150.0, "biological_atp": 15.0, "somatic_mass": 100.0}
    time_history = [0.0]
    history = {k: [v] for k, v in agent.get_diagnostics().items()}

    print_telemetry_line(0, {}, agent.get_diagnostics())
    print("-" * 85)

    for step in range(1, steps + 1):
        # Harsh radioactive decay environment, followed by nutrition recovery
        radiation = 3.5 if step < (steps // 2) else 0.1
        food = 0.0 if step < (0.6 * steps) else 10.0
        inputs = {"food_available": food, "toxic_radiation": radiation}
        
        agent.step(dt, **inputs)
        
        diagnostics = agent.get_diagnostics()
        time_history.append(step * dt)
        for k, v in diagnostics.items():
            if k in history:
                history[k].append(v)
        
        if step % max(1, steps // 4) == 0 or step == steps:
            print_telemetry_line(step, inputs, diagnostics)
            
    print("="*85)
    plot_simulation_results("Astrobiological Organism", time_history, history, limits)


def interactive_menu():
    while True:
        print("\n" + "="*60)
        print("       AUTONOMIC COMPILER - INTERACTIVE SIMULATION SUITE")
        print("="*60)
        print("Select an isolated prototype to load:")
        print("1) Autonomous Mobile Robot (AMR) - Battery & Frame stress")
        print("2) Virtual AI Agent - Cognitive ATP & Request Backlog")
        print("3) Astrobiological Organism - Cellular Glycogen & Tissue Repair")
        print("4) Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            run_robot_simulation()
        elif choice == "2":
            run_ai_simulation()
        elif choice == "3":
            run_astrobiology_simulation()
        elif choice == "4":
            print("\nExiting. Thank you.")
            break
        else:
            print("\n[Error] Invalid choice. Please enter a number from 1 to 4.")


if __name__ == "__main__":
    interactive_menu()