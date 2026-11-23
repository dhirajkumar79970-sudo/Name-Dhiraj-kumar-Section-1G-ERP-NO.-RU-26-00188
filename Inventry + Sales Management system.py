"""
Inventory + Sales Management System
Rungta International Skills University - B.Tech CSE (PS No. 42)

Concepts used: CRUD, Dictionaries, Pandas, File Handling
Files used   : inventory.csv (ID, Name, Stock, Price)
               sales.csv     (ID, Quantity, Amount)
"""

import os
import pandas as pd

INVENTORY_FILE = "inventory.csv"
SALES_FILE = "sales.csv"

INVENTORY_COLS = ["ID", "Name", "Stock", "Price"]
SALES_COLS = ["ID", "Quantity", "Amount"]


# ---------------------------------------------------------------
# File handling helpers
# ---------------------------------------------------------------
def load_inventory():
    """Read inventory.csv. If the file is not there, make an empty one."""
    if not os.path.exists(INVENTORY_FILE):
        df = pd.DataFrame(columns=INVENTORY_COLS)
        df.to_csv(INVENTORY_FILE, index=False)
    df = pd.read_csv(INVENTORY_FILE)
    df["Stock"] = df["Stock"].astype(int)
    df["Price"] = df["Price"].astype(float)
    return df


def save_inventory(df):
    df.to_csv(INVENTORY_FILE, index=False)


def load_sales():
    """Read sales.csv. If the file is not there, make an empty one."""
    if not os.path.exists(SALES_FILE):
        df = pd.DataFrame(columns=SALES_COLS)
        df.to_csv(SALES_FILE, index=False)
    df = pd.read_csv(SALES_FILE)
    df["Quantity"] = df["Quantity"].astype(int)
    df["Amount"] = df["Amount"].astype(float)
    return df


def save_sales(df):
    df.to_csv(SALES_FILE, index=False)


def fmt(number):
    """Show 10.0 as 10 and 10.5 as 10.5 (looks cleaner on screen)."""
    number = float(number)
    if number == int(number):
        return str(int(number))
    return str(round(number, 2))


def generate_id(df):
    """First item is I101, then I102, I103 ..."""
    if df.empty:
        return "I101"
    last_number = max(int(i[1:]) for i in df["ID"])
    return "I" + str(last_number + 1)


def find_row(df, item_id):
    """Return the index of the item in the dataframe, or None."""
    matches = df.index[df["ID"] == item_id].tolist()
    if matches:
        return matches[0]
    return None


# ---------------------------------------------------------------
# CRUD functions (one function for each)
# ---------------------------------------------------------------
def add_item(name, stock, price):
    """CREATE - add a new item to inventory."""
    if name.strip() == "":
        print("Name cannot be empty.")
        return
    if stock < 0 or price < 0:
        print("Stock and price cannot be negative.")
        return

    df = load_inventory()
    new_id = generate_id(df)

    # dictionary for the new record
    record = {"ID": new_id, "Name": name.strip(), "Stock": stock, "Price": price}
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    save_inventory(df)

    print("Item added.")
    print(f"ID: {new_id} | {record['Name']} | Stock: {stock} | Price: {fmt(price)}")


def update_item(item_id, new_stock=None, new_price=None):
    """UPDATE - change stock and/or price of an item."""
    df = load_inventory()
    row = find_row(df, item_id)
    if row is None:
        print(f"Item ID {item_id} not found.")
        return

    if new_stock is not None:
        if new_stock < 0:
            print("Stock cannot be negative.")
            return
        df.loc[row, "Stock"] = new_stock
    if new_price is not None:
        if new_price < 0:
            print("Price cannot be negative.")
            return
        df.loc[row, "Price"] = new_price

    save_inventory(df)
    print("Item updated.")
    print(f"ID: {item_id} | {df.loc[row, 'Name']} | "
          f"Stock: {df.loc[row, 'Stock']} | Price: {fmt(df.loc[row, 'Price'])}")


def delete_item(item_id):
    """DELETE - remove an item from inventory."""
    df = load_inventory()
    row = find_row(df, item_id)
    if row is None:
        print(f"Item ID {item_id} not found.")
        return

    name = df.loc[row, "Name"]
    df = df.drop(row).reset_index(drop=True)
    save_inventory(df)
    print(f"Item deleted: {item_id} ({name})")


def sell_item(item_id, quantity):
    """SELL - reduce stock and record the sale in sales.csv."""
    df = load_inventory()
    row = find_row(df, item_id)
    if row is None:
        print(f"Item ID {item_id} not found.")
        return
    if quantity <= 0:
        print("Quantity must be at least 1.")
        return

    available = int(df.loc[row, "Stock"])
    if quantity > available:
        print(f"Not enough stock. Available: {available}")
        return

    name = df.loc[row, "Name"]
    amount = quantity * df.loc[row, "Price"]

    # reduce the stock
    df.loc[row, "Stock"] = available - quantity
    save_inventory(df)

    # write the sale to sales.csv
    sales = load_sales()
    sale = {"ID": item_id, "Quantity": quantity, "Amount": amount}
    sales = pd.concat([sales, pd.DataFrame([sale])], ignore_index=True)
    save_sales(sales)

    left = available - quantity
    print(f"Sale recorded: {name} x{quantity} = {fmt(amount)}")
    if left == 0:
        print("Stock left: 0 | Item is now out of stock.")
    else:
        print(f"Stock left: {left}")


# ---------------------------------------------------------------
# Sales report (uses groupby)
# ---------------------------------------------------------------
def sales_report():
    sales = load_sales()
    if sales.empty:
        print("No sales recorded yet.")
        return

    inventory = load_inventory()
    # dictionary of ID -> Name, so we can show names in the report
    names = dict(zip(inventory["ID"], inventory["Name"]))

    report = sales.groupby("ID").agg(Units=("Quantity", "sum"),
                                     Revenue=("Amount", "sum")).reset_index()
    report["Name"] = report["ID"].map(names).fillna(report["ID"])  # deleted item -> show ID
    report = report.sort_values(by="Units", ascending=False)

    for _, r in report.iterrows():
        print(f"{r['Name']}: {r['Units']} units | Revenue: {fmt(r['Revenue'])}")

    print(f"Total revenue: {fmt(report['Revenue'].sum())}")
    best = report.iloc[0]
    print(f"Best seller: {best['Name']} ({best['Units']} units)")


# ---------------------------------------------------------------
# Input helpers (so the program does not crash on wrong input)
# ---------------------------------------------------------------
def ask_int(message):
    try:
        return int(input(message))
    except ValueError:
        print("Please enter a whole number.")
        return None


def ask_float(message):
    try:
        return float(input(message))
    except ValueError:
        print("Please enter a valid number.")
        return None


# ---------------------------------------------------------------
# Menu
# ---------------------------------------------------------------
def show_menu():
    print("\n===== Inventory + Sales Management =====")
    print("1. Add item")
    print("2. Sell")
    print("3. Update")
    print("4. Delete")
    print("5. Sales report")
    print("6. Exit")


def main():
    while True:
        show_menu()
        choice = input("Enter option: ").strip()

        if choice == "1":
            name = input("Name: ")
            stock = ask_int("Stock: ")
            price = ask_float("Price: ")
            if stock is not None and price is not None:
                add_item(name, stock, price)

        elif choice == "2":
            item_id = input("ID: ").strip().upper()
            qty = ask_int("Quantity: ")
            if qty is not None:
                sell_item(item_id, qty)

        elif choice == "3":
            item_id = input("ID: ").strip().upper()
            stock_text = input("New stock (press Enter to skip): ").strip()
            price_text = input("New price (press Enter to skip): ").strip()
            try:
                new_stock = int(stock_text) if stock_text else None
                new_price = float(price_text) if price_text else None
            except ValueError:
                print("Please enter valid numbers.")
                continue
            update_item(item_id, new_stock, new_price)

        elif choice == "4":
            item_id = input("ID: ").strip().upper()
            delete_item(item_id)

        elif choice == "5":
            sales_report()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Choose 1 to 6.")


if __name__ == "__main__":
    main()