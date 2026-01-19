"""Physics module for the simulation system.

This module contains the physics calculations and update logic
for the particle simulation.
"""


class PhysicsEngine:
    """Handles physics calculations for the simulation."""
    
    def __init__(self, config):
        """Initialize physics engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
    
    def apply_gravity(self, particle):
        """Apply gravity to a particle.
        
        Args:
            particle: Particle dictionary with position, velocity, mass
        """
        if not self.config.enable_gravity:
            return
        
        # Apply gravity in the last dimension (e.g., z-axis in 3D)
        if self.config.dimensions > 0:
            particle['velocity'][-1] -= self.config.gravity_constant * self.config.timestep
    
    def update_position(self, particle):
        """Update particle position based on velocity.
        
        Args:
            particle: Particle dictionary with position, velocity
        """
        for i in range(self.config.dimensions):
            particle['position'][i] += particle['velocity'][i] * self.config.timestep
    
    def apply_boundaries(self, particle):
        """Apply boundary conditions (elastic collision with walls).
        
        Args:
            particle: Particle dictionary with position, velocity
        """
        for i in range(self.config.dimensions):
            if particle['position'][i] < 0:
                particle['position'][i] = 0
                particle['velocity'][i] = abs(particle['velocity'][i])
            elif particle['position'][i] > self.config.boundary_size:
                particle['position'][i] = self.config.boundary_size
                particle['velocity'][i] = -abs(particle['velocity'][i])
    
    def update_particle(self, particle):
        """Update a single particle.
        
        Args:
            particle: Particle dictionary
        """
        self.apply_gravity(particle)
        self.update_position(particle)
        self.apply_boundaries(particle)
    
    def step(self, state):
        """Perform one physics step for all particles.
        
        Args:
            state: SimulationState object
        """
        for particle in state.particles:
            self.update_particle(particle)
        
        state.update_iteration()
