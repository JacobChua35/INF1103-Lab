def main():
    inventory, history = load_inventory()   # NEW
    tax = 0
    failedEntries = 0
    deliveriesProcessed = 0

    print("==============================")
    print("=== Daily Delivery Auditor ===")
    print("==============================")
    print()
    print(f"Starting Inventory: {inventory}")   # NEW
    print("Enter stock quantity for each delivery, or type 'quit' to finish.\n")

    while True:
        result = getValidInput()

        if result is False:
            break
        elif result is None:
            failedEntries += 1
            continue

        quantity = result
        inventory = processDelivery(inventory, quantity)
        tax += calculateTax(quantity)
        deliveriesProcessed += 1
        history.append(quantity)   # NEW

        if inventory > 500:
            print(f"\nCurrent Inventory: {inventory}. Exceeded 500 units! Halting entry process now.\n")
            break
        elif inventory == 500:
            print(f"\nCurrent Inventory: {inventory}. Inventory at its maximum capacity. Halting entry process now.\n")
            break

    generateReport(inventory, deliveriesProcessed, tax, failedEntries)
    save_inventory(inventory, history)   # NEW


def load_inventory():   # NEW
    try:
        with open("inventory.txt", "r") as file:
            total = int(file.readline())
            line = file.readline().strip()
            history = []
            if line != "":
                for item in line.split(","):
                    history.append(int(item))
            return total, history
    except (FileNotFoundError, ValueError):
        return 0, []


def save_inventory(total, history):   # NEW
    with open("inventory.txt", "w") as file:
        file.write(str(total) + "\n")
        file.write(",".join(str(item) for item in history))
    print("Inventory saved to inventory.txt")


def getValidInput():
    stock = input("Enter stock quantity: ").strip()   # CHANGED

    if stock.lower() == "quit":
        return False

    if stock.isdecimal():   # CHANGED
        return int(stock)

    print("=============================")
    print(f"Error! {stock} is not a valid number! Please enter an integer")
    print("=============================")
    return None


def processDelivery(currentTotal, newValue):
    return currentTotal + newValue


def calculateTax(amount):
    return amount * 0.1


def generateReport(totalUnits, deliveriesProcessed, totalTax, failedAttempts):
    print("=== End of Session Report ===")
    print(f"Total amount of Inventory: {totalUnits}")
    print(f"Total Deliveries Processed: {deliveriesProcessed}")
    print(f"Total Tax Collected: {totalTax:.2f}")
    print("=============================")
    print(f"Number of Failed/Rejected Entries: {failedAttempts}")
    print("=============================")


main()
