# SpatialGP Command Line Options Guide

This guide provides comprehensive documentation for all command line options available in the SpatialGP evolutionary programming system.

## Basic Usage

```bash
python run.py [OPTIONS]
```

## Command Line Options

### Core Experiment Options

#### `-config <path>`
Specifies the configuration file to use for the experiment.
- **Default**: `config.ini`
- **Example**: `python run.py -config Configs/LGP1/I107.ini`

#### `-seed <number>`
Sets the random seed for reproducible experiments.
- **Example**: `python run.py -seed 42`

#### `-generations <number>`
Overrides the number of generations specified in the config file.
- **Example**: `python run.py -generations 500`

### Output Options

#### `-output <path>`
Specifies the path for the best program output file.
- **Example**: `python run.py -output results/best_program.py`

#### `-pickle <path>`
Specifies the path for the pickled object output file. This model object can be unpickled and used or even further evolved in a later time.
- **Example**: `python run.py -pickle results/best_model.sgp`

#### `-evo <path>`
Specifies the path for the evolutionary statistics output file.
- **Example**: `python run.py -evo results/evolution_stats.csv`

#### `-pop_save_path <path>`
Specifies the directory where population pickle files are saved.
- **Example**: `python run.py -pop_save_path Output/Population/`

#### `-save_output`
Saves current experiment files in a timestamped directory under "Saved Experiments".
- **Example**: `python run.py -save_output`

### Checkpointing Options

#### `-cp`
Enables checkpointing mechanism to resume evolution from saved population.
- **Example**: `python run.py -cp`
- **Note**: Useful for long-running experiments that may be interrupted

### Analysis and Testing Options

#### `-analyze <path>`
Analyzes a given pickled SGP model and generates visualizations.
- **Example**: `python run.py -analyze Output/best.sgp`

#### `-test_model <path>`
Interactively tests a pickled model with manual inputs.
- **Example**: `python run.py -test_model Output/best.sgp`

#### `-formulize <path>`
Converts a pickled SGP model into mathematical equations (if applicable).
- **Example**: `python run.py -formulize Output/best.sgp`

#### `-compare <directory>`
Compares multiple evolution files and returns statistics about the best runs.
- **Example**: `python run.py -compare experiment_results/`
- **Note**: Uses optimization goal from config.ini

### Validation Options

#### `-validateConfig <directory>`
Tests the validity of all configuration files in a directory by running short experiments.
- **Example**: `python run.py -validateConfig Configs/LGP1/`
- **Note**: Runs each config for 3 generations to check for errors

### HPCC (High Performance Computing Cluster) Options

#### `-hpcc`
Runs the application as a single experiment on HPCC with interactive setup.
- **Example**: `python run.py -hpcc`
- **Interactive prompts for**:
  - Experiment title
  - Job time (hours)
  - Number of repetitions
  - Number of generations
  - Starting seed
  - Config file
  - Checkpointing preference

#### `-hpccExperiment`
Runs multiple HPCC experiments using all config files in a directory.
- **Example**: `python run.py -hpccExperiment`
- **Interactive prompts for**:
  - Experiment title (appended with config name)
  - Job time (hours)
  - Number of repetitions
  - Number of generations
  - Starting seed
  - Config directory
  - Checkpointing preference

## Example Commands

### Basic Experiment
```bash
# Run with default config
python run.py

# Run with custom config and seed
python run.py -config Configs/LGP1/I107.ini -seed 123
```

### Custom Output Paths
```bash
python run.py -config myconfig.ini -output my_best.py -pickle my_best.sgp -evo my_stats.csv
```

### Analysis Workflow
```bash
# Run experiment
python run.py -config experiment.ini -save_output

# Analyze results
python run.py -analyze Output/best.sgp

# Test the model
python run.py -test_model Output/best.sgp

# Convert to mathematical formula
python run.py -formulize Output/best.sgp
```

### Validation and Comparison
```bash
# Validate all configs in a directory
python run.py -validateConfig Configs/LGP1/

# Compare multiple experiment results
python run.py -compare experiment_results/
```

### HPCC Batch Processing
```bash
# Single HPCC experiment
python run.py -hpcc

# Multiple HPCC experiments from config directory
python run.py -hpccExperiment
```

### Resuming Interrupted Experiments
```bash
# Enable checkpointing for long experiments
python run.py -config longrun.ini -cp
```

## Notes

1. **File Paths**: Always use absolute paths or paths relative to the SpatialGP root directory.

2. **Config Override**: Command line arguments override corresponding values in configuration files.

3. **Output Files**: Default output files are stored in the `Output/` directory.

4. **HPCC Setup**: HPCC options are specifically designed for MSU's High Performance Computing Cluster and require proper environment setup.

5. **Interactive Mode**: Some options like `-hpcc` and `-hpccExperiment` require interactive input during execution.

6. **Validation**: Use `-validateConfig` to test configuration files before running full experiments.
