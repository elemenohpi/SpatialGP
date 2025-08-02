# Source Code for Spatial Genetic Programming

This repository contains the source code for Spatial Genetic Programming. There are five branches, each corresponding to one of the five different experiments conducted using this framework.

## Documentation

📖 **[Configuration and Experiment Guide](CONFIGURATION_GUIDE.md)** - Comprehensive guide for setting up and running experiments

🔧 **[Command Line Options Guide](COMMAND_LINE_GUIDE.md)** - Complete reference for all command line options

⚡ **[Quick Reference](QUICK_REFERENCE.md)** - Common commands and settings at a glance

🛠️ **[Custom Problems Guide](CUSTOM_PROBLEMS_GUIDE.md)** - Creating custom operators and fitness functions for new problems

## Quick Start

### Basic Usage
```bash
# Run with default configuration
python run.py

# Run with custom configuration
python run.py -config Configs/LGP1/I107.ini

# Run with specific seed for reproducibility
python run.py -seed 42 -generations 100
```

### Validate Configuration
```bash
# Test configuration files before running full experiments
python run.py -validateConfig Configs/LGP1/
```

### Analyze Results
```bash
# Analyze the best evolved model
python run.py -analyze Output/best.sgp

# Test model with manual inputs
python run.py -test_model Output/best.sgp
```

## Reference
For more detailed information about the general implementation, please refer to the following paper:
- [Spatial Genetic Programming](https://link.springer.com/chapter/10.1007/978-3-031-29573-7_17)

Additional information regarding the theoretical aspects of this project will be available as soon as it is published.

## Current State

### Implementation
The code base in this repository represents a prototype of the Spatial Genetic Programming (SGP) system. Ongoing work includes:
- Parallelizing the algorithm.
- Refining the system to function more effectively as a framework.

### Features and Research
Current research and development efforts focus on:
- Implementing Neural Network nodes to replace the underlying Linear Genetic Programming (LGP) structures.
- Enhancing performance through neuro-evolution (NE).

The NE-SGP code will be linked here once it is made publicly available.
