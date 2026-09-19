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
