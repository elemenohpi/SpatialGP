# Source Code for Spatial Genetic Programming

This repository contains the source code for Spatial Genetic Programming. There are five branches, each corresponding to one of the five different experiments conducted using this framework.

## Reference
For more detailed information about the general implementation, please refer to the following paper:
- [Spatial Genetic Programming Framework](https://link.springer.com/chapter/10.1007/978-3-031-29573-7_17)

Additional information regarding the theoretical aspects of this project will be available as soon as it is published.

## Experiment Setup

To conduct an experiment, it is essential to properly configure the `config.ini` file. This file should accurately reflect the modules required, including:
- The fitness/evaluation/problem file
- The traverse cost function

## Running the Experiment

To start the evolution process, execute the `run.py` script:

```bash
python run.py
```

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
