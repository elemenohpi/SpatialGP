# SpatialGP Configuration and Experiment Guide

This comprehensive guide explains how to configure and run experiments with the SpatialGP evolutionary programming system.

## Table of Contents
1. [Overview](#overview)
2. [Configuration File Structure](#configuration-file-structure)
3. [Setting Up an Experiment](#setting-up-an-experiment)
4. [Running Experiments](#running-experiments)
5. [Available Fitness Functions](#available-fitness-functions)
6. [Advanced Configuration](#advanced-configuration)
7. [Output Analysis](#output-analysis)
8. [Troubleshooting](#troubleshooting)

## Overview

SpatialGP is a custom evolutionary genetic programming system that evolves programs arranged in spatial topologies. The system uses Linear Genetic Programming (LGP) as the underlying program representation and supports various spatial arrangements and evolutionary operators.

## Configuration File Structure

Configuration files use INI format and are divided into several sections:

### General Evolutionary Configurations

```ini
######################################## General Evolutionary Configurations ########################################

# Fitness function to use (see Available Fitness Functions section)
fitness = Loop.AB5

# Random seed for reproducibility
seed = 101

# Number of evolutionary generations
generations = 100

# Population size
population_size = 300

# Tournament size for selection
tournament_size = 10

# Mutation rates
structural_mutation_rate = 0.40  # Spatial structure mutations (40%)
lgp_mutation_rate = 0.20         # LGP program mutations (20%)
return_mutation_rate_increase_handle = 0  # Additional mutation on return statements

# Crossover rate (0.0 to 1.0)
crossover_rate = 0

# Number of best individuals preserved each generation
elitism = 3

# Cost formula for spatial movement
# Available variables: distance, max_distance, length, max_length, return_val
cost_formula = math.log(1+distance)

# Spatial topology options: circle, ring, line, lattice
topology = circle

# Output node selection
# Options: single (one output), none (no designated output), 0.0-1.0 (percentage)
output_ratio = single

# Number of evaluation attempts per model
evaluation_count = 10
```

### Function/Input Set Configurations

```ini
######################################## Function/Input Set Configurations #########################################

# Available operator collections
basemath = OP_SUM, OP_DIV, OP_MULT, OP_MINUS  # Basic math operations
if = OP_IF                                      # Conditional operations
end_program = OP_END                           # Program termination
assign = OP_ASSIGN                             # Variable assignment
ant = LEFT, RIGHT, MOVE, IF_SENSE              # Ant navigation (for ant problems)

# Conditional operators
conditionals = ==, >, <

# Available constants
constants = 1

# Active operator sets (comma-separated)
operators = basemath, assign

# Number of internal registers
registers = 4
```

### SGP (Spatial Genetic Programming) Configurations

```ini
######################################## SGP Configurations #########################################

# Program initialization size range
init_size_min = 1
init_size_max = 5

# Maximum number of programs per individual
size_max = 10

# Loop configurations
enable_loops = True
self_loop = False
revisit_penalty = 0.01

# Maximum evaluation time per model (milliseconds)
max_evaluation_time = 100
```

### LGP (Linear Genetic Programming) Configurations

```ini
######################################## LGP Configurations #########################################

# Conditional return statements
conditional_return = 0
conditional_return_depth = 1

# LGP program size constraints
init_lgp_size_min = 1
init_lgp_size_max = 5
lgp_size_max = 10
```

### Spatial Configurations

```ini
######################################## Spatial Configurations #########################################

# Initial spatial arrangement radius
init_radius = 150
```

### System Configurations

```ini
######################################## SGP System Configurations #########################################

# System module selection (for advanced users)
individual = BaseIndividual
population = BasePopulation
interpreter = BaseInterpreter
evolver = BaseEvolver
programs = LGP

# Output file paths
best_program = Output/best.py
best_object = Output/best.sgp
pop_save_path = Output/Population/
evo_file = Output/evo.csv

# Additional options
save_annotation = False
```

## Setting Up an Experiment

### 1. Choose or Create a Configuration File

Start with an existing template:
- Use `config.ini` for general experiments
- Use `LGP_template.ini` for symbolic regression problems
- Browse `Configs/` directory for problem-specific configurations

### 2. Configure the Fitness Function

Set the `fitness` parameter to match your problem:

```ini
# For Feynman physics equations
fitness = Feynman6.II242

# For loop/control problems
fitness = Loop.AB5

# For regression tasks
fitness = Regression.YourProblem

# For simple test problems
fitness = SimpleProblem.SimpleProblem
```

### 3. Adjust Evolutionary Parameters

Key parameters to consider:

```ini
# For quick testing
generations = 10
population_size = 50

# For thorough search
generations = 1000
population_size = 500

# For symbolic regression, include advanced math operators
basemath = OP_SUM, OP_DIV, OP_MULT, OP_MINUS, OP_EXP, OP_SQRT, OP_SIN, OP_COS, OP_LOG
constants = 1, 2, 3, 5, -1
```

### 4. Configure Spatial Topology

Choose topology based on your problem:

```ini
# For local search behaviors
topology = line

# For global connectivity
topology = circle

# For grid-based problems
topology = lattice
```

## Running Experiments

### Basic Experiment

```bash
# Run with default configuration
python run.py

# Run with custom configuration
python run.py -config Configs/LGP1/I107.ini

# Set random seed for reproducibility
python run.py -config myconfig.ini -seed 42
```

### Experiment with Custom Parameters

```bash
# Override generations and output paths
python run.py -config myconfig.ini -generations 500 -output results/best.py -evo results/stats.csv
```

### Checkpointing for Long Experiments

```bash
# Enable checkpointing to resume interrupted experiments
python run.py -config longrun.ini -cp
```

### Save Results Automatically

```bash
# Automatically save results with timestamp
python run.py -config myconfig.ini -save_output
```

## Available Fitness Functions

### Built-in Problems

#### 1. Feynman Physics Equations
- **Location**: `Fitness/Feynman/`, `Fitness/Feynman1/` through `Fitness/Feynman10/`
- **Usage**: `fitness = Feynman6.II242`
- **Description**: Physics equations from Feynman lectures

#### 2. Loop/Control Problems
- **Location**: `Fitness/Loop/`
- **Usage**: `fitness = Loop.AB5`
- **Description**: Problems involving loops and control structures

#### 3. Regression Problems
- **Location**: `Fitness/Regression/`
- **Usage**: `fitness = Regression.YourProblem`
- **Description**: General regression tasks

#### 4. Control Problems
- **Location**: `Fitness/ControlProblem/`
- **Usage**: `fitness = ControlProblem.YourProblem`
- **Description**: Control system problems

#### 5. Custom Games
- **Location**: `Fitness/CustomGames/`
- **Usage**: `fitness = CustomGames.YourGame`
- **Description**: Game-playing problems

#### 6. Simple Test Problems
- **Location**: `Fitness/SimpleProblem.py`
- **Usage**: `fitness = SimpleProblem.SimpleProblem`
- **Description**: Basic test problems (e.g., circle area calculation)

### Creating Custom Fitness Functions

To create a custom fitness function:

1. Create a new Python file in the appropriate `Fitness/` subdirectory
2. Inherit from `AbstractFitness`
3. Implement required methods:

```python
from Fitness.AbstractFitness import AbstractFitness

class MyProblem(AbstractFitness):
    def settings(self):
        return {
            "optimization_goal": "min"  # or "max"
        }
    
    def inputs(self):
        return {
            "x": "float",
            "y": "float"
        }
    
    def outputs(self):
        return {
            "result": "float"
        }
    
    def evaluate(self, individual):
        # Your evaluation logic here
        pass
```

## Advanced Configuration

### Custom Operator Sets

Define custom operators by modifying the operators section:

```ini
# Enable specific operator collections
operators = basemath, assign, if

# For symbolic regression
basemath = OP_SUM, OP_DIV, OP_MULT, OP_MINUS, OP_EXP, OP_SQRT, OP_SIN, OP_COS, OP_LOG

# For control problems
operators = basemath, assign, if
```

### Cost Function Customization

Customize spatial movement costs:

```ini
# Simple distance-based cost
cost_formula = math.log(1+distance)

# Include program length penalty
cost_formula = math.log(1+distance) + 0.1*length

# Include return value consideration
cost_formula = math.log(1+distance) + math.log(1+abs(return_val))
```

### Topology Selection

Different topologies for different problem types:

```ini
# Linear arrangement - good for sequential problems
topology = line

# Circular arrangement - good for cyclic behaviors
topology = circle

# Ring topology - balance between local and global search
topology = ring

# Grid arrangement - good for 2D spatial problems
topology = lattice
```

## Output Analysis

### Generated Output Files

After running an experiment, check the `Output/` directory:

- **`best.sgp`**: Pickled best individual (for analysis)
- **`best.py`**: Python representation of best program
- **`evo.csv`**: Evolution statistics (fitness over generations)
- **`stats.csv`**: Detailed population statistics
- **`diversity.csv`**: Diversity metrics
- **`Population/`**: Saved population states (if checkpointing enabled)

### Analysis Commands

```bash
# Analyze the best model
python run.py -analyze Output/best.sgp

# Test model interactively
python run.py -test_model Output/best.sgp

# Convert to mathematical equations
python run.py -formulize Output/best.sgp

# Compare multiple experiment results
python run.py -compare experiment_directory/
```

### Visualization

The analysis command generates various visualizations:
- Spatial arrangement of programs
- Evolution curves
- Model structure diagrams
- Performance metrics

## Troubleshooting

### Common Issues

#### 1. Configuration Validation Errors
```bash
# Test configuration files before running full experiments
python run.py -validateConfig Configs/LGP1/
```

#### 2. Out of Memory Errors
- Reduce `population_size`
- Reduce `size_max` and `lgp_size_max`
- Reduce `max_evaluation_time`

#### 3. Slow Evolution
- Increase `structural_mutation_rate` for more exploration
- Decrease `population_size` for faster generations
- Reduce `evaluation_count`

#### 4. Poor Results
- Increase `generations`
- Increase `population_size`
- Adjust operator sets for your problem
- Try different `topology` settings
- Increase `elitism` to preserve good solutions

### Configuration Validation

Always validate new configurations:

```bash
# Validate single configuration
python run.py -config newconfig.ini -generations 3

# Validate multiple configurations
python run.py -validateConfig Configs/NewExperiments/
```

### Debugging Evolution

Monitor evolution progress:
- Check `evo.csv` for fitness trends
- Use `-analyze` to understand best individuals
- Compare results with `-compare` command

## Best Practices

1. **Start Small**: Begin with small populations and few generations for testing
2. **Use Seeds**: Always set random seeds for reproducible experiments
3. **Save Results**: Use `-save_output` for important experiments
4. **Validate First**: Test configurations with `-validateConfig` before full runs
5. **Monitor Progress**: Check evolution files during long runs
6. **Use Checkpointing**: Enable `-cp` for experiments longer than a few hours
7. **Document Changes**: Keep notes about configuration modifications

## Example Experiment Workflows

### Symbolic Regression Workflow
```bash
# 1. Configure for symbolic regression
cp LGP_template.ini my_regression.ini
# Edit fitness function and operators

# 2. Validate configuration
python run.py -validateConfig . my_regression.ini

# 3. Run experiment
python run.py -config my_regression.ini -seed 42 -save_output

# 4. Analyze results
python run.py -analyze Output/best.sgp
python run.py -formulize Output/best.sgp
```

### Comparative Study Workflow
```bash
# 1. Create multiple configurations
# 2. Run experiments with different seeds
for seed in {1..10}; do
    python run.py -config experiment.ini -seed $seed -evo results/evo_$seed.csv
done

# 3. Compare results
python run.py -compare results/
```

This guide provides the foundation for configuring and running experiments with SpatialGP. For specific problem domains, refer to the example configurations in the `Configs/` directory.
