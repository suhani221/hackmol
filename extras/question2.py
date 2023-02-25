import random

# Set the size of the grid
grid_size = 4
# Set the starting position to the center of the grid
position = (grid_size // 2, grid_size // 2)
# Set the target position to the prize state (grid point 15)
target = (grid_size - 1, grid_size - 1)
# Set the maximum number of steps for the simulation
max_steps = 10000
# Initialize the number of steps to reach the target to zero
num_steps = 0

# Simulate the random walk until the target is reached or the maximum number of steps is reached
while position != target and num_steps < max_steps:
    # Generate a random move (up, down, left, or right)
    move = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
    # Update the position based on the move
    new_position = tuple(sum(x) for x in zip(position, move))
    # Check if the new position is within the grid boundaries
    if 0 <= new_position[0] < grid_size and 0 <= new_position[1] < grid_size:
        # Update the position if it is within the boundaries
        position = new_position
    # Increment the number of steps
    num_steps += 1

# Print the result of the simulation
if position == target:
    print(f"The target was reached in {num_steps} steps.")
else:
    print(f"The target was not reached in {max_steps} steps.")
