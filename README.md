# 99.py - Modular Simulation System

3rd year of prompting and second semester of .py mechanics.

## Overview

This repository demonstrates a **complex simulation system** that's decomposed into separate modules instead of a single .py file. The main goal is to observe how .py systems can be reconfigured through a modular architecture.

## Architecture

The simulation system is divided into the following modules:

### Core Modules

1. **config.py** - Configuration Module
   - Manages all simulation parameters
   - Allows runtime reconfiguration
   - Provides default settings with easy customization

2. **state.py** - State Management Module
   - Handles simulation state (particles, iterations, status)
   - Manages initialization and updates
   - Tracks dynamic data throughout simulation

3. **physics.py** - Physics Engine Module
   - Implements physics calculations
   - Handles gravity, movement, and boundary conditions
   - Updates particle positions and velocities

4. **utils.py** - Utilities Module
   - Provides helper functions for statistics
   - Logging and formatting utilities
   - Reusable across different parts of the system

5. **main.py** - Main Entry Point
   - Orchestrates module initialization
   - Demonstrates the reconfigurable architecture
   - Shows module independence

## How It Works

The system demonstrates modular design principles:

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Loose Coupling**: Modules communicate through well-defined interfaces
3. **Reconfigurability**: Parameters can be changed without modifying code
4. **Reusability**: Modules can be used independently or together

## Usage

Run the simulation:

```bash
python main.py
```

This will:
- Load all modules at initialization
- Run a particle simulation with physics
- Display statistics at regular intervals
- Demonstrate reconfiguration capabilities
- Show module independence

## Reconfiguration Examples

The system can be easily reconfigured:

```python
import config

# Modify configuration
config.config.update(
    particle_count=50,
    gravity_constant=5.0,
    max_iterations=500
)
```

## Module Independence

Each module can be used independently:

```python
# Use just the config module
import config
custom_config = config.SimulationConfig()
custom_config.update(particle_count=10)

# Use just the utils module
import utils
utils.log_message("Custom message", "INFO")
```

## Key Features

- ✅ Modular architecture with separated concerns
- ✅ Easy reconfiguration without code changes
- ✅ Independent, reusable modules
- ✅ Clear initialization flow from main.py
- ✅ Demonstrates .py system reconfiguration principles 
