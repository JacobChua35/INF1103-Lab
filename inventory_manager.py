# inventory = [
#     {"ID": "P001","Name": "Laptop","Price":"$1200.00","Stock":"15"},
#     {"ID": "P002","Name": "Mouse","Price":"$25.50","Stock":"40"},
#     {"ID": "P003","Name": "Keyboard","Price":"$45.00","Stock":"25"}
# ]
    
import json
import os
import re

FILENAME = "inventory.json"

def load_inventory():
    """Load inventory from JSON file if it exists, else return an empty list."""
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return []

def save_inventory(inventory_list):
    """Save inventory to JSON file."""
    with open(FILENAME, "w") as f:
        json.dump(inventory_list, f, indent=4)
    print("Inventory saved successfully.")

inventory = load_inventory()   # replaces the hardcoded list


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


def displayAll():
    print("---------------------------------------------------------------------")
    for item in inventory:
        print(f"ID: {item['ID']} | Name: {item['Name']} | Price: ${item['Price']} | Stock: {item['Stock']}")
    print("---------------------------------------------------------------------")


def add_product():
    print("Add New Product")
    existing_ids = [item['ID'] for item in inventory]
    
    while True:
        product_id = input("Enter Product ID (format: P001): ").strip().upper()
        #Use Regex to validate the product ID format
        if not re.fullmatch(r"P\d{3}", product_id):
            print("Invalid Product ID format. Please use the format PXXX (e.g., P001).")
        elif product_id in existing_ids:
            print("Product ID already exists. Please use a unique ID.")
        else:
            break
    
    name = input("Enter Product Name: ").strip()
    price = input("Enter Product Price: ").strip()
    stock = input("Enter Product Stock Quantity: ").strip()

    new_product = {
        "ID": product_id,
        "Name": name,
        "Price": price,
        "Stock": stock
    }
    
    inventory.append(new_product)
    print()
    print("Product added successfully.")



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


