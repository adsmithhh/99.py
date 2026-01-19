"""Main entry point for the modular simulation system.

This demonstrates how a complex simulation system can be decomposed
into separate modules and called at initialization, showing how
.py systems can be reconfigured.
"""

# Import all modules at initialization
import config
import state
import physics
import utils


def run_simulation():
    """Run the simulation with modular components."""
    print("=" * 60)
    print("MODULAR SIMULATION SYSTEM")
    print("Demonstrating how .py systems can be reconfigured")
    print("=" * 60)
    
    # Initialize configuration module
    print("\n[1] Loading Configuration Module...")
    sim_config = config.config
    sim_config.display()
    
    # Initialize state module
    print("[2] Loading State Management Module...")
    sim_state = state.SimulationState(sim_config)
    sim_state.initialize()
    
    # Initialize physics module
    print("\n[3] Loading Physics Engine Module...")
    physics_engine = physics.PhysicsEngine(sim_config)
    
    # Run simulation loop
    print("\n[4] Starting Simulation Loop...")
    print(f"Running for {sim_config.max_iterations} iterations...\n")
    
    # Show initial statistics
    stats = utils.calculate_statistics(sim_state)
    utils.print_statistics(stats)
    
    # Run a few iterations with output
    display_interval = sim_config.max_iterations // 5
    
    for i in range(sim_config.max_iterations):
        physics_engine.step(sim_state)
        
        # Display statistics at intervals
        if (i + 1) % display_interval == 0:
            stats = utils.calculate_statistics(sim_state)
            utils.print_statistics(stats)
    
    # Final statistics
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    final_stats = utils.calculate_statistics(sim_state)
    utils.print_statistics(final_stats)
    
    # Show that we can reconfigure the system
    print("\n" + "=" * 60)
    print("RECONFIGURATION DEMO")
    print("=" * 60)
    print("\nReconfiguring system with different parameters...")
    sim_config.update(
        particle_count=50,
        gravity_constant=5.0,
        max_iterations=500
    )
    sim_config.display()
    
    print("System reconfigured! Ready for next run with new parameters.")
    print("\nThis demonstrates the modular, reconfigurable architecture:")
    print("  - config.py: Configuration parameters")
    print("  - state.py: State management")
    print("  - physics.py: Physics calculations")
    print("  - utils.py: Utility functions")
    print("  - main.py: Orchestration and initialization")


def demonstrate_module_independence():
    """Demonstrate that modules can be used independently."""
    print("\n" + "=" * 60)
    print("MODULE INDEPENDENCE DEMO")
    print("=" * 60)
    
    # Use config module independently
    print("\n[Config Module] Creating custom configuration...")
    custom_config = config.SimulationConfig()
    custom_config.update(particle_count=10, dimensions=2)
    custom_config.display()
    
    # Use utils module independently
    print("[Utils Module] Testing utility functions...")
    utils.log_message("This is an info message", "INFO")
    utils.log_message("This is a warning", "WARNING")
    
    print("\nModules are independent and reusable!")


if __name__ == "__main__":
    # Run the main simulation
    run_simulation()
    
    # Demonstrate module independence
    demonstrate_module_independence()
    
    print("\n" + "=" * 60)
    print("All demonstrations complete!")
    print("=" * 60)
