# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "polars==1.38.1",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", auto_download=["html"])


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from datetime import date
    from pathlib import Path

    # A molab GitHub mirror copies this notebook and not the CSV files.
    # If a file is already here, leave it. If it is missing, write the sample.
    _sample_files = {
        "menu.csv": """item,price,category
latte,4.50,drink
muffin,3.00,food
drip coffee,2.25,drink
bagel,2.50,food
cappuccino,3.75,drink
cold brew,4.25,drink
""",
        "sales.csv": """date,item,quantity,employee
2026-03-02,latte,4,ava
2026-03-02,muffin,2,ava
2026-03-02,drip coffee,8,ben
2026-03-02,bagel,3,ben
2026-03-02,cappuccino,2,cam
2026-03-02,cold brew,2,cam
2026-03-03,latte,6,ava
2026-03-03,cappuccino,2,ava
2026-03-03,drip coffee,4,ben
2026-03-03,muffin,3,ben
2026-03-03,bagel,2,ben
2026-03-04,latte,3,ava
2026-03-04,cold brew,4,ava
2026-03-04,drip coffee,6,ben
2026-03-04,bagel,4,ben
2026-03-04,muffin,2,cam
2026-03-04,cappuccino,2,cam
2026-03-05,latte,5,ava
2026-03-05,muffin,4,ava
2026-03-05,drip coffee,4,ben
2026-03-05,cold brew,3,ben
2026-03-05,cappuccino,3,ben
2026-03-06,latte,2,ava
2026-03-06,bagel,2,ava
2026-03-06,drip coffee,8,ben
2026-03-06,muffin,2,ben
2026-03-06,cold brew,3,cam
2026-03-06,cappuccino,1,cam
""",
        "hours.csv": """employee,date,hours
ava,2026-03-02,6.0
ava,2026-03-03,6.0
ava,2026-03-04,5.5
ava,2026-03-05,6.0
ava,2026-03-06,4.0
ben,2026-03-02,5.0
ben,2026-03-03,5.0
ben,2026-03-04,6.0
ben,2026-03-05,5.5
ben,2026-03-06,5.0
cam,2026-03-02,4.0
cam,2026-03-04,4.0
cam,2026-03-06,5.0
""",
    }

    def _ensure_csvs():
        folders = []
        try:
            folders.append(Path(__file__).resolve().parent)
        except NameError:
            pass
        try:
            folders.append(Path(mo.notebook_location()))
        except Exception:
            pass
        cwd = Path.cwd()
        if cwd not in folders:
            folders.append(cwd)
        for folder in folders:
            if all((folder / name).exists() for name in _sample_files):
                return folder
        for folder in folders:
            try:
                for name, text in _sample_files.items():
                    path = folder / name
                    if not path.exists():
                        path.write_text(text)
                return folder
            except OSError:
                continue
        raise RuntimeError("Could not find or create the CSV files")

    here = _ensure_csvs()
    return date, here, mo, pl


@app.cell
def _(mo):
    mo.md(r"""
    # MIS 501 — Lecture 10: Dataframes
    ### In-class exercise — the coffee shop terminal

    Same coffee shop. The register is a small menu:

    1. **Take an order** — the order loop from last week. Each line is saved
       onto the end of `sales.csv`
    2. **View menu** — the menu table, just the drinks, and prices with tax
    3. **Show reports** — totals from `sales.csv` and `hours.csv`
    4. **Quit**

    A **dataframe** is the whole table: columns have names, and every row is
    one record. [Polars](https://pola.rs) reads the CSV for you.

    The demo cell, the order helpers, and `append_sales` are already written.
    Fill in the report functions. Do not change the run cell at the bottom.

    **View menu**

    1. `drinks_only(menu)` — keep rows where `category` is `"drink"` (`filter`)
    2. `with_tax(menu, rate)` — add a `price_with_tax` column (`with_columns`).
       Round to 2 decimals. Alabama's rate from last week is 4%, so a latte
       is `4.50 * 1.04 = 4.68`

    **Show reports** — each sales row is one line on a ticket. `quantity` is
    how many of that item were sold, so a total is the **sum of quantity**,
    not a count of rows.

    3. `quantity_by_item(sales)` — one row per `item`, with the total
       `quantity`, highest first (`group_by`)
    4. `revenue_by_day(sales, menu)` — join the menu on `item` so each sale
       picks up its `price`, then total revenue (`quantity * price`) for
       each `date`
    5. `hours_by_employee(hours)` — total `hours` for each `employee`,
       highest first

    **Bonus** — Show reports prints this too.

    6. `revenue_per_hour(sales, menu, hours)` — one row per employee for the
       week: their revenue, their hours, and `revenue / hours`
    """)
    return


@app.cell
def _(here, pl):
    # sales.csv is one row per line on a ticket. hours.csv is one row per shift.
    _sales_preview = pl.read_csv(here / "sales.csv")
    print(_sales_preview.head(3))
    print("sales rows:", _sales_preview.height)
    _hours_preview = pl.read_csv(here / "hours.csv")
    print(_hours_preview.head(3))
    return


@app.cell
def _(here, pl):
    # A dataframe is the table. Column names come from the header row.
    # Names that start with _ stay in this cell, so they don't clash with the run cell.
    _menu = pl.read_csv(here / "menu.csv")
    print(_menu)
    print("columns:", _menu.columns)

    # The dictionary from last time, if you still want one
    _menu_items = dict(zip(_menu["item"], _menu["price"]))
    print(_menu_items)

    # filter keeps rows that pass a test
    _food = _menu.filter(pl.col("category") == "food")
    print(_food)

    # with_columns adds a column. The original price stays put.
    _doubled = _menu.with_columns((pl.col("price") * 2).alias("two_of_them"))
    print(_doubled.select("item", "price", "two_of_them"))

    # group_by collapses many rows into one row per key
    _sample_sales = pl.DataFrame(
        {
            "item": ["latte", "latte", "muffin"],
            "quantity": [2, 1, 3],
        }
    )
    print(
        _sample_sales.group_by("item")
        .agg(pl.col("quantity").sum().alias("quantity"))
        .sort("item")
    )

    # join looks up a column from another table
    _sample_prices = pl.DataFrame(
        {
            "item": ["latte", "muffin"],
            "price": [4.50, 3.00],
        }
    )
    print(_sample_sales.join(_sample_prices, on="item"))
    return


@app.function
# Task 1 — keep rows where category is "drink"
def drinks_only(menu):
    return menu.head(0)


@app.function
# Task 2 — add price_with_tax, rounded to 2 decimals. Keep the other columns.
def with_tax(menu, rate):
    return menu.head(0)


@app.function
# Task 3 — one row per item; quantity is the sum; highest quantity first
def quantity_by_item(sales):
    return pl.DataFrame({"item": [], "quantity": []})


@app.function
# Task 4 — join menu on item, then one row per date with total revenue
def revenue_by_day(sales, menu):
    return pl.DataFrame({"date": [], "revenue": []})


@app.function
# Task 5 — one row per employee; hours is the sum; highest hours first
def hours_by_employee(hours):
    return pl.DataFrame({"employee": [], "hours": []})


@app.function
# Bonus 6 — revenue, hours, and revenue / hours for each employee
def revenue_per_hour(sales, menu, hours):
    return pl.DataFrame(
        {
            "employee": [],
            "revenue": [],
            "hours": [],
            "revenue_per_hour": [],
        }
    )


@app.function
# last week — strip spaces and lowercase so " Latte " matches "latte"
def clean_item(item):
    return item.strip().lower()


@app.function
# last week — True if the item is a key in the menu dictionary
def is_on_menu(menu, item):
    if item in menu:
        return True
    else:
        return False


@app.function
# last week — convert text to a positive int; invalid input returns None
def parse_quantity(text):
    try:
        qty = int(text)
    except ValueError:
        return None
    if qty > 0:
        return qty
    else:
        return None


@app.function
# last week — keep asking until END; skip unknown items and bad quantities
def take_order(menu):
    order = []
    item = input("Please enter your order or type END to end your order: ")
    while clean_item(item) != "end":
        item = clean_item(item)
        if is_on_menu(menu, item):
            qty_text = input("How many? ")
            qty = parse_quantity(qty_text)
            if qty is None:
                print("Please enter a whole number greater than 0")
            else:
                order.append((item, qty))
        else:
            print(item + " is not on the menu. Please enter a valid menu item")
        item = input("Continue or type END to end your order: ")
    return order


@app.function
# last week — each order line is (item, qty); total is price * qty
def calculate_total(menu, order):
    total = 0.0
    for item, qty in order:
        total = total + menu[item] * qty
    return total


@app.function
# already written — add this order's rows onto the end of sales.csv
def append_sales(path, order, employee, sold_on):
    new_rows = pl.DataFrame(
        {
            "date": [sold_on for _item, _qty in order],
            "item": [item for item, _qty in order],
            "quantity": [qty for _item, qty in order],
            "employee": [employee for _item, _qty in order],
        }
    )
    sales = pl.read_csv(path)
    pl.concat([sales, new_rows]).write_csv(path)


@app.cell
def _(date, here, pl):
    # Run it — 1 take an order, 2 view the menu, 3 show reports, 4 quit
    def show_menu():
        menu = pl.read_csv(here / "menu.csv")
        print("Menu")
        print(menu)
        print()
        print("Drinks")
        print(drinks_only(menu))
        print()
        print("Menu with 4% tax")
        print(with_tax(menu, 0.04))

    def show_reports():
        menu = pl.read_csv(here / "menu.csv")
        sales = pl.read_csv(here / "sales.csv")
        hours = pl.read_csv(here / "hours.csv")
        print("Quantity by item")
        print(quantity_by_item(sales))
        print()
        print("Revenue by day")
        print(revenue_by_day(sales, menu))
        print()
        print("Hours by employee")
        print(hours_by_employee(hours))
        print()
        print("Revenue per hour")
        print(revenue_per_hour(sales, menu, hours))

    def ring_up_order():
        menu_df = pl.read_csv(here / "menu.csv")
        prices = dict(zip(menu_df["item"], menu_df["price"]))
        print(menu_df)
        employee = input("Employee name: ").strip().lower()
        if employee == "":
            print("Enter an employee name.")
            return
        order = take_order(prices)
        if order == []:
            print("No items. Nothing saved.")
            return
        sold_on = date.today().isoformat()
        append_sales(here / "sales.csv", order, employee, sold_on)
        subtotal = calculate_total(prices, order)
        tax = round(subtotal * 0.04, 2)
        print("You ordered:", order)
        print(f"Subtotal: ${subtotal:.2f}")
        print(f"Tax (4%): ${tax:.2f}")
        print(f"Total: ${subtotal + tax:.2f}")
        print("Saved to sales.csv")

    choice = ""
    while choice != "4":
        print()
        print("1. Take an order")
        print("2. View menu")
        print("3. Show reports")
        print("4. Quit")
        choice = input("Choose 1-4: ").strip()
        if choice == "1":
            ring_up_order()
        elif choice == "2":
            show_menu()
        elif choice == "3":
            show_reports()
        elif choice == "4":
            print("Goodbye")
        else:
            print("Please enter 1, 2, 3, or 4")
    return


if __name__ == "__main__":
    app.run()
