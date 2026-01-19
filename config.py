"""Configuration module for the simulation system.

This module handles configuration settings and parameters
that can be easily reconfigured without changing the core logic.
"""


class SimulationConfig:
    """Configuration class for simulation parameters."""
    
    def __init__(self):
        """Initialize default configuration."""
        self.timestep = 0.01
        self.max_iterations = 1000
        self.particle_count = 100
        self.dimensions = 3
        self.boundary_size = 100.0
        self.enable_collisions = True
        self.enable_gravity = True
        self.gravity_constant = 9.81
        
    def update(self, **kwargs):
        """Update configuration parameters.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: Unknown configuration parameter '{key}'")
    
    def display(self):
        """Display current configuration."""
        print("\n=== Simulation Configuration ===")
        print(f"Timestep: {self.timestep}")
        print(f"Max Iterations: {self.max_iterations}")
        print(f"Particle Count: {self.particle_count}")
        print(f"Dimensions: {self.dimensions}")
        print(f"Boundary Size: {self.boundary_size}")
        print(f"Collisions Enabled: {self.enable_collisions}")
        print(f"Gravity Enabled: {self.enable_gravity}")
        print(f"Gravity Constant: {self.gravity_constant}")
        print("================================\n")


# Global configuration instance
config = SimulationConfig()
