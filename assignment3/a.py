import matplotlib.pyplot as plt

# Sample data (X values and corresponding max and min values)
x_values = [1, 2, 3, 4, 5]
max_values = [10, 15, 7, 12, 18]
min_values = [5, 8, 4, 9, 11]

# Create the plot
plt.plot(x_values, max_values, label="Max Values", marker='o', linestyle = 'None',  color='blue')
plt.plot(x_values, min_values, label="Min Values", marker='o', linestyle = 'None',  color='red')

# Join max and min values with vertical lines
for x, ymax, ymin in zip(x_values, max_values, min_values):
    plt.vlines(x, ymin, ymax, colors='green', linestyles='dashed', linewidth = 6)

# Add labels, legend, and title
plt.xlabel('burst number')
plt.ylabel('bursts size')
plt.legend()
plt.title('AIMD bursts')

# Show the plot
plt.grid(True)
plt.savefig('cwnd.png')





