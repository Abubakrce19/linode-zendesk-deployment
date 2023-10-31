# filename: plot.py

import matplotlib.pyplot as plt
import numpy as np

# Create an array of x values from -10 to 10
x = np.linspace(-10, 10, 400)

# Create an array of y values which are the square of x values
y = x**2

# Create the plot
plt.plot(x, y)

# Add title and labels
plt.xlabel('x')
plt.ylabel('y')
plt.title('y = x^2')

# Show the plot
plt.show()