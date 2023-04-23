import matplotlib.pyplot as plt
import numpy as np

dataSize = 1000

# Make synthetic data:
xData = np.random.randint(100, size=dataSize)
yData = np.linspace(0, dataSize, num=dataSize, dtype=int)

# Make and show plot
plt.plot(xData, yData, '.k')
plt.show()
