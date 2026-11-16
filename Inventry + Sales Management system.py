
import csv
import os

INVENTORY_FILE = "inventory.csv"
SALES_FILE = "sales.csv"


# Create CSV files
def create_files():
    if not os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Stock", "Price"])

    if not os.path.exists(SALES_FILE):
        with open(SALES_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Quantity", "Amount"])


# Load inventory
def load_inventory():
    with open(INVENTORY_FILE, "r") as f:
        return list(csv.DictReader(f))


# Save inventory
def save_inventory(items):
    with open(INVENTORY_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["ID", "Name", "Stock", "Price"]
        )
        writer.writeheader()
        writer.writerows(items)


# 1. Add item
def add_item():
    items = load_inventory()

    item_id = input("Enter Item ID: ").strip()
    if any(x["ID"] == item_id for x in items):
        print("Item ID already exists.")
        return

    name = input("Enter Item Name: ").strip()

    try:
        stock = int(input("Enter Stock: "))
        price = float(input("Enter Price: "))

        if not item_id or not name or stock < 0 or price < 0:
            print("Invalid input.")
            return

    except ValueError:
        print("Please enter valid numbers.")
        return

    items.append({
        "ID": item_id,
        "Name": name,
        "Stock": str(stock),
        "Price": str(price)
    })

    save_inventory(items)
    print("Item added.")


# 2. Sell item
def sell_item():
    items = load_inventory()

    item_id = input("Enter Item ID: ").strip()

    item = next(
        (x for x in items if x["ID"] == item_id), None
    )

    if item is None:
        print(f"Item ID {item_id} not found.")
        return

    try:
        quantity = int(input("Enter Quantity: "))

        if quantity <= 0:
            print("Invalid quantity.")
            return

    except ValueError:
        print("Enter a valid quantity.")
        return

    available = int(item["Stock"])

    if quantity > available:
        print(f"Not enough stock. Available: {available}")
        return

    amount = quantity * float(item["Price"])

    item["Stock"] = str(available - quantity)
    save_inventory(items)

    with open(SALES_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([item_id, quantity, amount])

    print("Sale recorded.")
    print("Revenue:", amount)


# 3. Update item
def update_item():
    items = load_inventory()
    item_id = input("Enter Item ID: ").strip()

    for item in items:
        if item["ID"] == item_id:
            try:
                name = input("Enter New Name (Enter to skip): ")
                stock = input("Enter New Stock (Enter to skip): ")
                price = input("Enter New Price (Enter to skip): ")

                if name:
                    item["Name"] = name

                if stock:
                    if int(stock) < 0:
                        print("Stock cannot be negative.")
                        return
                    item["Stock"] = str(int(stock))

                if price:
                    if float(price) < 0:
                        print("Price cannot be negative.")
                        return
                    item["Price"] = str(float(price))

                save_inventory(items)
                print("Item updated.")
                return

            except ValueError:
                print("Invalid input.")
                return

    print(f"Item ID {item_id} not found.")


# 4. Delete item
def delete_item():
    items = load_inventory()
    item_id = input("Enter Item ID: ").strip()

    updated_items = [
        item for item in items if item["ID"] != item_id
    ]

    if len(items) == len(updated_items):
        print(f"Item ID {item_id} not found.")
        return

    save_inventory(updated_items)
    print("Item deleted.")


# 5. Sales report
def sales_report():
    items = load_inventory()

    with open(SALES_FILE, "r") as f:
        sales = list(csv.DictReader(f))

    quantities = {}
    revenues = {}
    total_revenue = 0

    names = {item["ID"]: item["Name"] for item in items}

    for sale in sales:
        item_id = sale["ID"]
        quantity = int(sale["Quantity"])
        amount = float(sale["Amount"])

        quantities[item_id] = quantities.get(item_id, 0) + quantity
        revenues[item_id] = revenues.get(item_id, 0) + amount
        total_revenue += amount

    print("\n--------- SALES REPORT ---------")

    for item_id in quantities:
        print("Item:", names.get(item_id, item_id))
        print("Units Sold:", quantities[item_id])
        print("Revenue:", revenues[item_id])
        print("-------------------------------")

    print("Total Revenue:", total_revenue)

    if quantities:
        best = max(quantities, key=quantities.get)
        print("Best Seller:", names.get(best, best))
        print("Units Sold:", quantities[best])


# 6. Display inventory
def show_inventory():
    items = load_inventory()

    print("\n--------- INVENTORY ---------")

    for item in items:
        print(
            item["ID"],
            item["Name"],
            "Stock:", item["Stock"],
            "Price:", item["Price"]
        )


# Main menu
def main():
    create_files()

    while True:
        print("\n===== INVENTORY MANAGEMENT SYSTEM =====")
        print("1. Add Item")
        print("2. Sell Item")
        print("3. Update Item")
        print("4. Delete Item")
        print("5. Sales Report")
        print("6. Show Inventory")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_item()

        elif choice == "2":
            sell_item()

        elif choice == "3":
            update_item()

        elif choice == "4":
            delete_item()

        elif choice == "5":
            sales_report()

        elif choice == "6":
            show_inventory()

        elif choice == "0":
            print("Thank you!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
