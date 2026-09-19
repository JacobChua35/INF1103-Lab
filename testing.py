"""
modular_auditor.py
Week 3: Modularized version of Week 2's auditor.py
"""

def get_valid_input():
    """
    Prompts for a stock quantity. Handles validation + 'quit' signal.

    In:  nothing
    Out: (value, is_valid, is_quit)
    """
    stock = input("Enter stock quantity: ")

    if stock.lower() == "quit":
        return None, False, True

    if stock.isdigit():
        quantity = int(stock)
        return quantity, True, False
    else:
        print(f"Error: '{stock}' is not a valid number. Please enter an integer.\n")
        return None, False, False


def process_delivery(current_total, new_value):
    """
    Adds a new delivery to the running total.

    In:  current_total (int), new_value (int)
    Out: new_total (int)
    """
    return current_total + new_value


def calculate_tax(amount):
    """
    Calculates tax for a single delivery (10%).

    In:  amount (int)
    Out: tax (float)
    """
    return amount * 0.10


def generate_report(total_units, total_tax, deliveries_processed, failed_attempts):
    """
    Prints the final summary report. No return value.
    """
    print("=== End of Session Report ===")
    print(f"Total amount of Inventory: {total_units}")
    print(f"Total Tax Collected: {total_tax:.2f}")
    print(f"Total Deliveries Processed: {deliveries_processed}")
    print("=============================")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")


def main():
    # 1. Initialize everything to zero at the start
    total_inventory = 0
    total_tax = 0.0
    deliveries_processed = 0
    failed_entries = 0

    print("==============================")
    print("=== Daily Delivery Auditor ===")
    print("==============================")
    print()
    print("Enter stock quantity for each delivery, or type 'quit' to finish.\n")

    # 2. Continuous loop until 'quit'
    while True:
        quantity, is_valid, is_quit = get_valid_input()

        if is_quit:
            break

        if not is_valid:
            failed_entries += 1
            continue

        # 3. Valid entry: update total, calculate tax, update counters
        total_inventory = process_delivery(total_inventory, quantity)
        total_tax += calculate_tax(quantity)
        deliveries_processed += 1

        # Inventory cap checks
        if total_inventory > 500:
            print(f"ALERT!: Current Inventory exceeds 500 units! Current Inventory: {total_inventory}")
            print("Halting entry process immediately.\n")
            break
        elif total_inventory == 500:
            print("Inventory is exactly at capacity (500 units).\n")

    # 4. Final report (printed once, after the loop ends)
    generate_report(total_inventory, total_tax, deliveries_processed, failed_entries)


if __name__ == "__main__":
    main()