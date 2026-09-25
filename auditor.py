
total_inventory = 0          
failed_entries = 0           

print("==============================")
print("=== Daily Delivery Auditor ===")
print("==============================")
print()
print("Enter stock quantity for each delivery, or type 'quit' to finish.\n")

while True:  # Requirement 2: loop until user types 'quit'
    stock = input("Enter stock quantity: ")

    # Exit condition
    if stock.lower() == "quit":
            break

    if stock.isdigit():
        quantity = int(stock)

            # Reject Negative Numbers
        if quantity < 0:
            print(f"Error: Negative quantity '{quantity}' is not allowed.\n")
            failed_entries += 1

        total_inventory += quantity

        # If Total Inventory > 500
        if total_inventory > 500:
            print(f"ALERT!: Current Inventory exceeds 500 units! Current Inventory: {total_inventory}")
            print("Halting entry process immediately.\n")
            break
        elif total_inventory == 500:
            print("Inventory is exactly at capacity (500 units).\n")

    else:
        print(f"Error: '{stock}' is not a valid number. Please enter an integer.\n")
        failed_entries += 1
        continue

    # Requirement 8: final report
    print("=== End of Session Report ===")
    print(f"Total amount of Inventory: {total_inventory}")
    print("=============================")
    print(f"Number of Failed/Rejected Entries: {failed_entries}")

