# Ask user for inputs
price = float(input("Input a Price : "))
grids = int(input("Input a How many Grid you want : "))
grid_percent = float(input("Input a gird % : "))

# Validate that number of grids is odd
if grids % 2 == 0:
    print("Number of grids must be odd. Please restart the program.")
else:
    step = price * (grid_percent / 100)  # Calculate step size

    # Generate and display each grid level
    for i in range(1, grids + 1):
        level = price + (i - 1) * step
        # Format output: if the value is an integer, print without decimal, else with 2 decimals
        if level.is_integer():
            print(f"grid {i} : {int(level)}")
        else:
            print(f"grid {i} : {level:.2f}")