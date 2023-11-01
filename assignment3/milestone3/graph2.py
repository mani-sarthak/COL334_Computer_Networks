import matplotlib.pyplot as plt
import numpy as np

# Data for the first graph
x1 = np.linspace(0, 10, 100)
y1 = np.sin(x1)

# Create the first figure and plot the first graph with a label
plt.figure(1)
plt.plot(x1, y1, label='Graph 1')
plt.title('Graph 1')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend()  # This will now find the artist with a label

# Data for the second graph
x2 = np.linspace(0, 10, 100)
y2 = np.cos(x2)

# Create the second figure and plot the second graph with a label
plt.figure(2)
plt.plot(x2, y2, label='Graph 2', color='red')
plt.title('Graph 2')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend()  # This will now find the artist with a label

# Show the first figure
plt.figure(1)
plt.savefig("man.png")

# # Show the second figure
# plt.figure(2)
# plt.show()
