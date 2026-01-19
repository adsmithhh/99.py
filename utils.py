"""Utilities module for the simulation system.

This module provides utility functions for logging, statistics,
and other helper functionality.
"""

import math


def calculate_statistics(state):
    """Calculate statistics about the current simulation state.
    
    Args:
        state: SimulationState object
        
    Returns:
        dict: Statistics dictionary
    """
    if not state.particles:
        return {}
    
    # Calculate average position
    avg_position = [0.0] * state.config.dimensions
    for particle in state.particles:
        for i in range(state.config.dimensions):
            avg_position[i] += particle['position'][i]
    
    for i in range(len(avg_position)):
        avg_position[i] /= len(state.particles)
    
    # Calculate average velocity magnitude
    avg_velocity = 0.0
    for particle in state.particles:
        vel_magnitude = math.sqrt(sum(v**2 for v in particle['velocity']))
        avg_velocity += vel_magnitude
    avg_velocity /= len(state.particles)
    
    return {
        'iteration': state.iteration,
        'particle_count': len(state.particles),
        'avg_position': avg_position,
        'avg_velocity': avg_velocity
    }


def print_statistics(stats):
    """Print simulation statistics.
    
    Args:
        stats: Statistics dictionary
    """
    if not stats:
        print("No statistics available")
        return
    
    print(f"\n--- Iteration {stats['iteration']} ---")
    print(f"Particles: {stats['particle_count']}")
    print(f"Avg Position: {[f'{x:.2f}' for x in stats['avg_position']]}")
    print(f"Avg Velocity: {stats['avg_velocity']:.2f}")


def log_message(message, level="INFO"):
    """Log a message with a level.
    
    Args:
        message: Message to log
        level: Log level (INFO, WARNING, ERROR)
    """
    print(f"[{level}] {message}")


def format_particle_info(particle):
    """Format particle information for display.
    
    Args:
        particle: Particle dictionary
        
    Returns:
        str: Formatted particle information
    """
    pos_str = ", ".join(f"{p:.2f}" for p in particle['position'])
    vel_str = ", ".join(f"{v:.2f}" for v in particle['velocity'])
    return f"Particle {particle['id']}: pos=[{pos_str}], vel=[{vel_str}], mass={particle['mass']:.2f}"
