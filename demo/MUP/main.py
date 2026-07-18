# Ask user for inputs
price = float(input("Input a Price : "))
grids = int(input("Input a How many Grid you want : "))
grid_percent = float(input("Input a gird % : "))

# Validate that number of grids is odd
if grids % 2 == 0:
    print("Number of grids must be odd. Please restart the program.")
else:
    step = price * (grid_percent / 100)  # Calculate step size
    middle_index = grids // 2  # Find the middle grid (0-based index)
    
    # Generate and display each grid level
    for i in range(1, grids + 1):
        level = price + (i - 1) * step
        
        # Determine if BUY, SELL, or no buy or sell
        if i - 1 < middle_index:
            # Grids BEFORE middle are BUY
            if level.is_integer():
                print(f"grid {i} : {int(level)} (BUY)")
            else:
                print(f"grid {i} : {level:.2f} (BUY)")
        elif i - 1 == middle_index:
            # Middle grid is no buy or sell
            if level.is_integer():
                print(f"grid {i} : {int(level)} (no buy or sell)")
            else:
                print(f"grid {i} : {level:.2f} (no buy or sell)")
        else:
            # Grids AFTER middle are SELL
            if level.is_integer():
                print(f"grid {i} : {int(level)} (SELL)")
            else:
                print(f"grid {i} : {level:.2f} (SELL)")