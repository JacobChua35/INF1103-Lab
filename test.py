def main():
    inventory = 0
    tax = 0
    failedEntries = 0
    deliveriesProcessed = 0
    
    print("==============================")
    print("=== Daily Delivery Auditor ===")
    print("==============================")
    print()
    print("Enter stock quantity for each delivery, or type 'quit' to finish.\n")
    
    while True:
        result = getValidInput()
        
        if result is False:
            break
        elif result is None:
            failedEntries += 1
            continue

        quantity = result
        inventory = processDelivery(inventory,quantity)
        tax += calculateTax(quantity)
        deliveriesProcessed += 1

        if inventory > 500:
            print()
            print(f"Current Inventory: {inventory}. Exceeed 500 units! Halting entry process now.")
            print()
            break
        elif inventory == 500:
            print()
            print(f"Current Inventory: {inventory}. Inventory at it\'s maximum capacity. Halting entry process now.")
            print()
            break
        
    generateReport(inventory,deliveriesProcessed,tax,failedEntries)
        
def getValidInput():
    stock = input("Enter stock quantity: ")
    
    if stock.lower() == "quit":
        return False
    
    if stock.isdigit():
        quantity = int(stock)
        return quantity
    else:
        print("=============================")
        print(f"Error! {stock} is not a valid number! Please enter an integer")
        print("=============================")
        return None
    
def processDelivery(currentTotal,newValue):
    return currentTotal + newValue
    
def calculateTax(amount):
    amount *= 0.1
    return amount  

def generateReport(totalUnits,deliveriesProcessed,totalTax,failedAttempts):
    print("=== End of Session Report ===")
    print(f"Total amount of Inventory: {totalUnits}")
    print(f"Total Deliveries Processed: {deliveriesProcessed}")
    print(f"Total Tax Collected: {totalTax:.2f}")
    print("=============================")
    print(f"Number of Failed/Rejected Entries: {failedAttempts}")
    print("=============================")

main()