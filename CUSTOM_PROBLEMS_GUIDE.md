# Creating Custom Functions and Fitness Problems for SpatialGP

This guide explains how to extend SpatialGP with custom operators and fitness functions for solving new problems not included in the base system.

## Table of Contents
1. [Overview](#overview)
2. [Creating Custom Operators](#creating-custom-operators)
3. [Creating Custom Fitness Functions](#creating-custom-fitness-functions)
4. [Complete Example: Quadratic Equation Problem](#complete-example-quadratic-equation-problem)
5. [Configuration Setup](#configuration-setup)
6. [Running Your Custom Experiment](#running-your-custom-experiment)
7. [Advanced Examples](#advanced-examples)
8. [Best Practices](#best-practices)

## Overview

To add a completely new problem to SpatialGP, you typically need to:

1. **Create custom operators** (if needed) - Mathematical or logical operations specific to your domain
2. **Create a fitness function** - Defines the problem and evaluates solution quality
3. **Configure the experiment** - Set up the evolutionary parameters and operator sets
4. **Run and analyze** - Execute the experiment and analyze results

## Creating Custom Operators

Custom operators extend the function set available to evolved programs. They inherit from `AbstractOperator` and define specific mathematical or logical operations.

### Basic Operator Structure

```python
# File: Operators/myoperators.py
import math
from Operators.AbstractOperator import AbstractOperator

class OP_POWER(AbstractOperator):
    def __init__(self):
        super().__init__()
    
    def eval(self, a):
        """
        Execute the operation with given arguments
        Args:
            a: List of input values
        Returns:
            Result of the operation
        """
        try:
            result = pow(a[0], a[1])
            # Handle overflow/underflow
            if abs(result) > 1e10:
                return 1e10 if result > 0 else -1e10
            return result
        except:
            return 0.0
    
    def demands(self):
        """
        Specify input types and count
        Returns:
            List of required input types
        """
        return ["float", "float"]
    
    def products(self):
        """
        Specify output types
        Returns:
            List of output types
        """
        return ["float"]
    
    def name(self):
        """
        Operator identifier
        """
        return "OP_POWER"
    
    def annotation(self):
        """
        String template for visualization
        """
        return "{} = {} ^ {}"
    
    @staticmethod
    def op_code():
        """
        Python code representation (optional)
        """
        code = """
def op_power(a, b):
    return pow(a, b)
"""
        return code
```

### Advanced Operator Example

```python
class OP_SIGMOID(AbstractOperator):
    def __init__(self):
        super().__init__()
    
    def eval(self, a):
        try:
            # Sigmoid function: 1 / (1 + e^(-x))
            x = a[0]
            if x > 500:  # Prevent overflow
                return 1.0
            elif x < -500:
                return 0.0
            return 1.0 / (1.0 + math.exp(-x))
        except:
            return 0.5  # Default middle value
    
    def demands(self):
        return ["float"]
    
    def products(self):
        return ["float"]
    
    def name(self):
        return "OP_SIGMOID"
    
    def annotation(self):
        return "{} = sigmoid({})"

class OP_GAUSSIAN(AbstractOperator):
    def __init__(self):
        super().__init__()
    
    def eval(self, a):
        try:
            # Gaussian: e^(-(x-mu)^2 / (2*sigma^2))
            x, mu, sigma = a[0], a[1], abs(a[2]) + 0.001  # Ensure sigma > 0
            return math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))
        except:
            return 0.0
    
    def demands(self):
        return ["float", "float", "float"]  # x, mu, sigma
    
    def products(self):
        return ["float"]
    
    def name(self):
        return "OP_GAUSSIAN"
    
    def annotation(self):
        return "{} = gaussian({}, {}, {})"
```

## Creating Custom Fitness Functions

Fitness functions define the problem to be solved and evaluate how well evolved programs perform.

### Basic Fitness Structure

```python
# File: Fitness/MyProblem/QuadraticSolver.py
import math
import random
from Fitness.AbstractFitness import AbstractFitness

class QuadraticSolver(AbstractFitness):
    def __init__(self):
        super().__init__()
        self.test_cases = self.generate_test_cases()
    
    def settings(self):
        """
        Define optimization settings
        """
        return {
            "optimization_goal": "min"  # "min" or "max"
        }
    
    def inputs(self):
        """
        Define input variables and their types
        """
        return {
            "a": "float",  # coefficient of x^2
            "b": "float",  # coefficient of x
            "c": "float",  # constant term
            "x": "float"   # variable
        }
    
    def outputs(self):
        """
        Define expected outputs
        """
        return {
            "y": "float"  # result of ax^2 + bx + c
        }
    
    def generate_test_cases(self):
        """
        Generate test cases for the problem
        """
        test_cases = []
        for _ in range(50):  # 50 test cases
            a = random.uniform(-5, 5)
            b = random.uniform(-5, 5)
            c = random.uniform(-5, 5)
            x = random.uniform(-10, 10)
            expected_y = a * x * x + b * x + c
            test_cases.append((a, b, c, x, expected_y))
        return test_cases
    
    def evaluate(self, individual):
        """
        Evaluate how well the individual solves the problem
        """
        total_error = 0.0
        successful_evaluations = 0
        
        for a, b, c, x, expected_y in self.test_cases:
            inputs = [a, b, c, x]
            
            try:
                # Get the individual's output
                predicted_y = individual.evaluate(inputs)
                
                if predicted_y is None:
                    continue
                
                # Calculate error
                error = abs(expected_y - predicted_y)
                total_error += error
                successful_evaluations += 1
                
            except Exception as e:
                continue
        
        if successful_evaluations == 0:
            return float('inf')  # Worst possible fitness
        
        # Return average error (lower is better)
        return total_error / successful_evaluations
    
    def preprocess(self, individual):
        """
        Optional: Preprocessing before evaluation
        """
        pass
    
    def postprocess(self, individual):
        """
        Optional: Postprocessing after evaluation
        """
        pass
```

### Advanced Fitness Example with Data Loading

```python
# File: Fitness/TimeSeries/StockPredictor.py
import numpy as np
import pandas as pd
from Fitness.AbstractFitness import AbstractFitness

class StockPredictor(AbstractFitness):
    def __init__(self):
        super().__init__()
        self.data = self.load_data()
        self.train_data, self.test_data = self.split_data()
    
    def settings(self):
        return {
            "optimization_goal": "max"  # Maximize correlation
        }
    
    def inputs(self):
        return {
            "price_t1": "float",    # Price at t-1
            "price_t2": "float",    # Price at t-2
            "volume": "float",      # Trading volume
            "rsi": "float"          # Relative Strength Index
        }
    
    def outputs(self):
        return {
            "predicted_price": "float"
        }
    
    def load_data(self):
        """
        Load your dataset (replace with actual data loading)
        """
        # Example: Load from CSV
        # return pd.read_csv('data/stock_data.csv')
        
        # For demonstration, generate synthetic data
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', periods=1000)
        prices = 100 + np.cumsum(np.random.randn(1000) * 0.5)
        volumes = np.random.randint(1000, 10000, 1000)
        
        return pd.DataFrame({
            'date': dates,
            'price': prices,
            'volume': volumes
        })
    
    def split_data(self):
        """
        Split data into training and testing sets
        """
        split_idx = int(len(self.data) * 0.8)
        return self.data[:split_idx], self.data[split_idx:]
    
    def calculate_rsi(self, prices, window=14):
        """
        Calculate Relative Strength Index
        """
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.convolve(gains, np.ones(window)/window, mode='valid')
        avg_losses = np.convolve(losses, np.ones(window)/window, mode='valid')
        
        rs = avg_gains / (avg_losses + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def evaluate(self, individual):
        """
        Evaluate prediction accuracy
        """
        predictions = []
        actuals = []
        
        prices = self.train_data['price'].values
        volumes = self.train_data['volume'].values
        rsi_values = self.calculate_rsi(prices)
        
        # Start from index 16 to have enough history for RSI
        for i in range(16, len(prices) - 1):
            try:
                inputs = [
                    prices[i-1],      # price_t1
                    prices[i-2],      # price_t2
                    volumes[i],       # volume
                    rsi_values[i-16]  # rsi
                ]
                
                predicted = individual.evaluate(inputs)
                if predicted is None:
                    continue
                
                predictions.append(predicted)
                actuals.append(prices[i+1])  # Next day's actual price
                
            except:
                continue
        
        if len(predictions) < 10:  # Minimum predictions required
            return -1.0  # Poor fitness
        
        # Calculate correlation coefficient
        correlation = np.corrcoef(predictions, actuals)[0, 1]
        return correlation if not np.isnan(correlation) else -1.0
```

## Complete Example: Quadratic Equation Problem

Let's create a complete working example that evolves programs to solve quadratic equations.

### Step 1: Create Custom Operators (if needed)

```python
# File: Operators/quadratic_ops.py
import math
from Operators.AbstractOperator import AbstractOperator

class OP_SQUARE(AbstractOperator):
    def __init__(self):
        super().__init__()
    
    def eval(self, a):
        result = a[0] * a[0]
        return min(max(result, -1e10), 1e10)  # Bound the result
    
    def demands(self):
        return ["float"]
    
    def products(self):
        return ["float"]
    
    def name(self):
        return "OP_SQUARE"
    
    def annotation(self):
        return "{} = {}^2"
```

### Step 2: Create the Fitness Function

```python
# File: Fitness/CustomProblems/QuadraticEquation.py
import random
import math
from Fitness.AbstractFitness import AbstractFitness

class QuadraticEquation(AbstractFitness):
    def __init__(self):
        super().__init__()
        # Generate diverse test cases
        self.test_cases = []
        random.seed(42)  # For reproducible test cases
        
        for _ in range(100):
            a = random.uniform(-3, 3)
            b = random.uniform(-5, 5)
            c = random.uniform(-5, 5)
            x = random.uniform(-5, 5)
            expected = a * x * x + b * x + c
            self.test_cases.append((a, b, c, x, expected))
    
    def settings(self):
        return {
            "optimization_goal": "min"
        }
    
    def inputs(self):
        return {
            "a": "float",
            "b": "float",
            "c": "float",
            "x": "float"
        }
    
    def outputs(self):
        return {
            "result": "float"
        }
    
    def evaluate(self, individual):
        total_error = 0.0
        valid_evaluations = 0
        
        for a, b, c, x, expected in self.test_cases:
            inputs = [a, b, c, x]
            
            try:
                result = individual.evaluate(inputs)
                if result is None:
                    continue
                
                error = abs(expected - result)
                total_error += error
                valid_evaluations += 1
                
                # Early termination if error is too large
                if error > 1000:
                    total_error += 1000  # Penalty for large errors
                
            except:
                total_error += 1000  # Penalty for failed evaluations
        
        if valid_evaluations == 0:
            return 10000  # Very poor fitness
        
        # Return Root Mean Square Error
        rmse = math.sqrt(total_error / len(self.test_cases))
        return rmse
```

### Step 3: Create Configuration File

```ini
# File: quadratic_experiment.ini

######################################## General Evolutionary Configurations ########################################
fitness = CustomProblems.QuadraticEquation
seed = 42
generations = 200
population_size = 200
tournament_size = 7
structural_mutation_rate = 0.30
lgp_mutation_rate = 0.25
crossover_rate = 0.1
elitism = 5
cost_formula = math.log(1+distance)
topology = circle
output_ratio = single
evaluation_count = 1

######################################## Function/Input Set Configurations #########################################
# Include basic math and custom operators
basemath = OP_SUM, OP_DIV, OP_MULT, OP_MINUS
quadratic_ops = OP_SQUARE
assign = OP_ASSIGN
end_program = OP_END

# Use custom operators
operators = basemath, quadratic_ops, assign

# Constants that might be useful
constants = 0, 1, 2, -1, 0.5

# No conditionals needed for this problem
conditionals = None

# Number of registers
registers = 6

######################################## SGP Configurations #########################################
init_size_min = 2
init_size_max = 8
size_max = 15
enable_loops = False
self_loop = False
max_evaluation_time = 50

######################################## LGP Configurations #########################################
conditional_return = 0
init_lgp_size_min = 3
init_lgp_size_max = 10
lgp_size_max = 20

######################################## Spatial Configurations #########################################
init_radius = 100

######################################## SGP System Configurations #########################################
individual = BaseIndividual
population = BasePopulation
interpreter = BaseInterpreter
evolver = BaseEvolver
programs = LGP

best_program = Output/quadratic_best.py
best_object = Output/quadratic_best.sgp
evo_file = Output/quadratic_evo.csv
save_annotation = True
```

## Configuration Setup

### Directory Structure

Create the following directory structure for your custom problem:

```
SpatialGP/
├── Operators/
│   └── quadratic_ops.py          # Your custom operators
├── Fitness/
│   └── CustomProblems/
│       └── QuadraticEquation.py  # Your fitness function
├── Configs/
│   └── Custom/
│       └── quadratic_experiment.ini  # Your configuration
└── quadratic_experiment.ini      # Main config file
```

### Verify Directory Creation

```bash
# Create directories
mkdir -p Fitness/CustomProblems
mkdir -p Operators
mkdir -p Configs/Custom
```

## Running Your Custom Experiment

### Step 1: Validate Configuration

```bash
# Test the configuration first
python run.py -validateConfig . -config quadratic_experiment.ini
```

### Step 2: Run Short Test

```bash
# Quick test with few generations
python run.py -config quadratic_experiment.ini -generations 5 -population_size 20
```

### Step 3: Full Experiment

```bash
# Run the full experiment
python run.py -config quadratic_experiment.ini -save_output
```

### Step 4: Analyze Results

```bash
# Analyze the best solution
python run.py -analyze Output/quadratic_best.sgp

# Test the model interactively
python run.py -test_model Output/quadratic_best.sgp

# Convert to mathematical formula
python run.py -formulize Output/quadratic_best.sgp
```

## Advanced Examples

### Classification Problem

```python
# File: Fitness/Classification/IrisClassifier.py
import random
from sklearn.datasets import load_iris
from Fitness.AbstractFitness import AbstractFitness

class IrisClassifier(AbstractFitness):
    def __init__(self):
        super().__init__()
        self.data = load_iris()
        self.X = self.data.data
        self.y = self.data.target
        
    def settings(self):
        return {"optimization_goal": "max"}  # Maximize accuracy
    
    def inputs(self):
        return {
            "sepal_length": "float",
            "sepal_width": "float", 
            "petal_length": "float",
            "petal_width": "float"
        }
    
    def outputs(self):
        return {"class_prediction": "float"}
    
    def evaluate(self, individual):
        correct = 0
        total = len(self.X)
        
        for i in range(total):
            inputs = list(self.X[i])
            prediction = individual.evaluate(inputs)
            
            if prediction is None:
                continue
                
            # Convert continuous output to class (0, 1, or 2)
            predicted_class = int(round(max(0, min(2, prediction))))
            
            if predicted_class == self.y[i]:
                correct += 1
        
        return correct / total  # Accuracy
```

### Time Series Prediction

```python
# File: Fitness/TimeSeries/SineWavePredictor.py
import math
import numpy as np
from Fitness.AbstractFitness import AbstractFitness

class SineWavePredictor(AbstractFitness):
    def __init__(self):
        super().__init__()
        # Generate sine wave data with noise
        self.time_steps = np.linspace(0, 4*np.pi, 200)
        self.values = np.sin(self.time_steps) + 0.1*np.random.randn(200)
        
    def settings(self):
        return {"optimization_goal": "min"}
    
    def inputs(self):
        return {
            "t_minus_3": "float",
            "t_minus_2": "float", 
            "t_minus_1": "float",
            "current_time": "float"
        }
    
    def outputs(self):
        return {"next_value": "float"}
    
    def evaluate(self, individual):
        errors = []
        
        # Use sliding window to predict next value
        for i in range(3, len(self.values)-1):
            inputs = [
                self.values[i-3],
                self.values[i-2],
                self.values[i-1],
                self.time_steps[i]
            ]
            
            prediction = individual.evaluate(inputs)
            if prediction is None:
                continue
                
            actual = self.values[i+1]
            error = (prediction - actual) ** 2
            errors.append(error)
        
        if not errors:
            return 1000
        
        return math.sqrt(sum(errors) / len(errors))  # RMSE
```

## Best Practices

### 1. Operator Design
- **Handle edge cases**: Always check for division by zero, overflow, etc.
- **Bound outputs**: Prevent infinite or NaN values
- **Keep it simple**: Start with basic operators before adding complexity
- **Test independently**: Test operators outside of evolution first

### 2. Fitness Function Design
- **Use diverse test cases**: Cover the full problem space
- **Handle failures gracefully**: Return reasonable fitness for failed evaluations
- **Scale appropriately**: Ensure fitness values are in reasonable ranges
- **Consider efficiency**: Avoid expensive operations in tight loops

### 3. Configuration
- **Start conservative**: Begin with smaller populations and fewer generations
- **Validate first**: Always test configurations before full runs
- **Document parameters**: Comment your configuration choices
- **Save results**: Use `-save_output` for important experiments

### 4. Debugging
- **Test incrementally**: Start with simple cases
- **Check outputs**: Use `-test_model` to verify behavior
- **Monitor evolution**: Watch fitness progression in CSV files
- **Use visualization**: Analyze evolved models with `-analyze`

### 5. Experiment Design
- **Multiple runs**: Use different seeds for statistical significance
- **Parameter sweeps**: Try different evolutionary parameters
- **Comparative studies**: Compare against baseline methods
- **Document everything**: Keep detailed notes about experiments

## Common Pitfalls

1. **Unbounded operators**: Always handle overflow/underflow
2. **Poor test cases**: Ensure comprehensive coverage of problem space
3. **Inappropriate fitness scaling**: Very large or small fitness values can cause issues
4. **Insufficient validation**: Test configurations thoroughly before full runs
5. **Ignoring failed evaluations**: Handle cases where individual.evaluate() returns None

## Example Command Sequence

Here's a complete workflow for creating and running a custom experiment:

```bash
# 1. Create directories
mkdir -p Fitness/MyProblem
mkdir -p Operators/MyOperators

# 2. Create your files (operators, fitness, config)
# ... (copy your custom code) ...

# 3. Validate configuration
python run.py -validateConfig . -config my_experiment.ini

# 4. Quick test
python run.py -config my_experiment.ini -generations 3 -population_size 10

# 5. Full experiment
python run.py -config my_experiment.ini -save_output

# 6. Analysis
python run.py -analyze Output/best.sgp
python run.py -formulize Output/best.sgp

# 7. Compare multiple runs
python run.py -compare "Saved Experiments/"
```

This guide provides everything needed to extend SpatialGP with custom problems. Start with simple examples and gradually increase complexity as you become more familiar with the system.
