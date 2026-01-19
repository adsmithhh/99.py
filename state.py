"""State management module for the simulation system.

This module handles the state of the simulation including
particle positions, velocities, and other dynamic data.
"""

import random


class SimulationState:
    """Manages the state of the simulation."""
    
    def __init__(self, config):
        """Initialize simulation state.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.iteration = 0
        self.particles = []
        self.is_running = False
        
    def initialize(self):
        """Initialize particle positions and velocities."""
        print("Initializing simulation state...")
        self.particles = []
        
        for i in range(self.config.particle_count):
            particle = {
                'id': i,
                'position': [
                    random.uniform(0, self.config.boundary_size)
                    for _ in range(self.config.dimensions)
                ],
                'velocity': [
                    random.uniform(-1, 1)
                    for _ in range(self.config.dimensions)
                ],
                'mass': random.uniform(0.5, 2.0)
            }
            self.particles.append(particle)
        
        self.iteration = 0
        self.is_running = True
        print(f"Initialized {len(self.particles)} particles")
    
    def get_status(self):
        """Get current simulation status.
        
        Returns:
            dict: Status information
        """
        return {
            'iteration': self.iteration,
            'particle_count': len(self.particles),
            'is_running': self.is_running
        }
    
    def update_iteration(self):
        """Increment iteration counter."""
        self.iteration += 1
    
    def stop(self):
        """Stop the simulation."""
        self.is_running = False
        print("Simulation stopped")
