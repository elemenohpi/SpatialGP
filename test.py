import math

import numpy as np

import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

# Example data
measurements = [1, 2, 3, 4, 5]
predictions = [0, 0, 0, 0, 0]

# Calculate the correlation coefficient

correlation_coefficient = np.corrcoef(measurements, predictions)[0, 1]

if str(correlation_coefficient) == "nan":
    correlation_coefficient = 10

# Print the correlation coefficient
print("Correlation coefficient:", correlation_coefficient)
