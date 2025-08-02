# SpatialGP Quick Reference

## Common Commands

### Basic Experiment
```bash
python run.py                                    # Default config
python run.py -config myconfig.ini               # Custom config
python run.py -seed 42 -generations 100         # Set seed and generations
```

### Configuration Testing
```bash
python run.py -validateConfig Configs/LGP1/     # Test all configs in directory
python run.py -config test.ini -generations 3   # Quick test of single config
```

### Output Control
```bash
python run.py -save_output                       # Auto-save with timestamp
python run.py -output best.py -evo stats.csv    # Custom output paths
```

### Analysis
```bash
python run.py -analyze Output/best.sgp          # Analyze best model
python run.py -test_model Output/best.sgp       # Interactive testing
python run.py -formulize Output/best.sgp        # Convert to equations
python run.py -compare results/                 # Compare multiple runs
```

### Long Experiments
```bash
python run.py -cp                               # Enable checkpointing
python run.py -config longrun.ini -cp -save_output
```

## Key Configuration Parameters

### Evolutionary Settings
```ini
fitness = Loop.AB5              # Problem to solve
seed = 101                      # Random seed
generations = 100               # Evolution length
population_size = 300           # Population size
tournament_size = 10            # Selection pressure
structural_mutation_rate = 0.40 # Spatial mutation rate
lgp_mutation_rate = 0.20       # Program mutation rate
elitism = 3                     # Best preserved
```

### Spatial Settings
```ini
topology = circle               # circle, ring, line, lattice
output_ratio = single          # single, none, or 0.0-1.0
cost_formula = math.log(1+distance)
init_radius = 150
```

### Operators
```ini
basemath = OP_SUM, OP_DIV, OP_MULT, OP_MINUS
operators = basemath, assign
constants = 1
registers = 4
```

## Common Problem Types

### Symbolic Regression
```ini
fitness = Feynman6.II242
basemath = OP_SUM, OP_DIV, OP_MULT, OP_MINUS, OP_EXP, OP_SQRT, OP_SIN, OP_COS, OP_LOG
constants = 1, 2, 3, 5, -1
```

### Control Problems
```ini
fitness = Loop.AB5
operators = basemath, assign, if
enable_loops = True
```

### Simple Test
```ini
fitness = SimpleProblem.SimpleProblem
operators = basemath, assign
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Out of memory | Reduce `population_size`, `size_max` |
| Slow evolution | Increase `structural_mutation_rate` |
| Poor results | Increase `generations`, `population_size` |
| Config errors | Use `-validateConfig` first |

## File Locations

- **Configs**: `Configs/LGP1/`, `Configs/SGP1/`, etc.
- **Templates**: `config.ini`, `LGP_template.ini`
- **Output**: `Output/best.sgp`, `Output/evo.csv`
- **Problems**: `Fitness/Feynman/`, `Fitness/Loop/`, etc.

## Output Files

- **`best.sgp`**: Best evolved model (pickled)
- **`best.py`**: Python code of best model
- **`evo.csv`**: Evolution statistics
- **`stats.csv`**: Population statistics
- **`diversity.csv`**: Diversity metrics
