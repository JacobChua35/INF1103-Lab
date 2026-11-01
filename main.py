from ast import main
import json
import os
import re

from product import Product
from inventory import Inventory

FILENAME = "inventory.json"

# ================= File handling (stays in main, not in the classes) =================

def load_inventory():
    """Load products from the JSON file into an Inventory object."""
    inventory = Inventory()
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
        
        for item in data:
            price = float(str(item["Price"]).replace("$", ""))
            stock = int(item["Stock"])
            inventory.add_product(Product(item["ID"], item["Name"], price, stock))
    return inventory

def save_inventory(inventory_list):
    """Convert every Product to a dict and save to the JSON file."""
    data = [product.to_dict() for product in inventory_list.get_all_products()]
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)
    print("Inventory saved successfully.")

# data = [
#     {"ID": "P001","Name": "Laptop","Price":"$1200.00","Stock":"15"},
#     {"ID": "P002","Name": "Mouse","Price":"$25.50","Stock":"40"},
#     {"ID": "P003","Name": "Keyboard","Price":"$45.00","Stock":"25"}
# ]

# ================= Input helpers =================
def get_product_id():
    """Ask for an ID and check the PXXX format. Returns None if invalid."""
    product_id = input("Enter Product ID (format: P001): ").strip().upper()
    if not re.fullmatch(r"P\d{3}", product_id):
        print("Invalid Product ID format. Please use the format PXXX (e.g., P001).")
        return None
    return product_id

def get_number(prompt, number_type):
    """Keep asking until the user types a valid non-negative number."""
    while True:
        try:
            value = number_type(input(prompt).strip().replace("$", ""))
            if value >= 0:
                return value
            print("Value cannot be negative.")
        except ValueError:
            print("Please enter a valid number.")
            
# ================= Menu =================
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
    
def add_product(inventory):
    print("Add New Product")
    while True:
        product_id = get_product_id()
        if product_id is None:
            continue
        if inventory.search_product(product_id) is not None:
            print("Product ID already exists. Please enter a unique ID.")
            continue
        break
    
    name = input("Enter Product Name: ").strip()
    price = get_number("Enter Product Price: ", float)
    stock = get_number("Enter Product Stock Quantity: ", int)
    
    inventory.add_product(Product(product_id,name,price,stock))
    print()
    print(f"Product {product_id} added successfully.")
    
def update_stock(inventory):
    print("Update Stock")
    product_id = get_product_id()
    if product_id is None:
        return

    product = inventory.search_product(product_id)
    
    if product is None:
        print("Product not found.")
        return
    
    print("Product Found:")
    product.display_details()
    new_stock = get_number("Enter New Stock Quantity: ", int)
    product.update_stock(new_stock)
    print()
    print("Stock updated successfully.")


def search_product(inventory):
    print("Search Product")
    product_id = get_product_id()
    if product_id is None:
        return

    product = inventory.search_product(product_id)
    if product is None:
        print()
        print("Product not found.")
    else:
        print("Product Found:")
        product.display_details()

        
    while True:
        menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
        elif choice == "6":
            save_inventory(inventory)  # Save inventory before exiting
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()