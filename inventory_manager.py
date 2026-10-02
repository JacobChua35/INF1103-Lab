

# inventory = [
#     {"ID": "P001","Name": "Laptop","Price":"$1200.00","Stock":"15"},
#     {"ID": "P002","Name": "Mouse","Price":"$25.50","Stock":"40"},
#     {"ID": "P003","Name": "Keyboard","Price":"$45.00","Stock":"25"}
# ]
    
def menu():
    print("=======================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=======================================")
    
    print("-------MENU-------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("------------------")

while True:
    menu()
    choice = input("Enter your choice (1-6): ").strip()
    
    if choice == "1":
        displayAll()
    elif choice == "2":
        add_product()
    elif choice == "3":
        update_stock()
    elif choice == "4":
        search_product()
    elif choice == "5":   
        save_inventory(inventory)
    elif choice == "6":
        save_inventory(inventory)  # Save inventory before exiting
        print("Exiting the program.")
        break
    else:
        print("Invalid choice. Please try again.")


