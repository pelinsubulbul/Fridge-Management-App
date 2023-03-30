import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry

# Database setup
conn = sqlite3.connect('fridge.db')
c = conn.cursor()
c.execute(
    '''CREATE TABLE IF NOT EXISTS groceries (id INTEGER PRIMARY KEY, item TEXT, quantity INTEGER, date_added TEXT, expiration_date TEXT)''')
conn.commit()
conn.close()


def execute_query(query, *params):
    with sqlite3.connect('fridge.db') as conn:
        c = conn.cursor()
        if query.startswith('INSERT'):
            # Insert a new item
            c.execute(query, params)
        elif query.startswith('UPDATE'):
            # Update the quantity of an existing item
            c.execute(query, params)
        elif query.startswith('DELETE'):
            # Delete an item
            c.execute(query, params)
        else:
            # Select items
            result = c.execute(query, params)
            return result

        conn.commit()


def update_treeview():
    grocery_tree.delete(*grocery_tree.get_children())
    rows = execute_query("SELECT * FROM groceries")
    for row in rows:
        grocery_tree.insert("", tk.END, values=row)


def add_command():
    item = item_text.get()
    quantity = quantity_text.get()
    date_added = datetime.now().strftime("%Y-%m-%d")
    expiration_date = cal.get()  # Use cal.get() instead of expiration_text.get()

    # Check if item, quantity, or expiration date input is empty or only contains whitespace
    if not item.strip() or not quantity.strip() or not expiration_date.strip():
        messagebox.showerror("Error", "Please enter a valid item, quantity, and expiration date.")
        return

    try:
        # Try to convert quantity to integer
        quantity = int(quantity)
    except ValueError:
        # Show error message if quantity is not a valid integer
        messagebox.showerror("Error", "Quantity must be a valid integer.")
        return

    # Check if item already exists in the database
    existing_item = execute_query("SELECT * FROM groceries WHERE item=?", item).fetchone()

    if existing_item:
        # Item already exists, so update the quantity
        new_quantity = existing_item[2] + quantity
        execute_query("UPDATE groceries SET quantity=? WHERE id=?", new_quantity, existing_item[0])
    else:
        # Item does not exist, so add it to the database
        execute_query("INSERT INTO groceries (item, quantity, date_added, expiration_date) VALUES (?, ?, ?, ?)", item,
                      quantity, date_added, expiration_date)

    update_treeview()


selected_tuple = None


def update_command():
    global selected_tuple
    if selected_tuple:
        try:
            item = item_text.get()
            quantity = int(quantity_text.get())
            expiration_date = cal.get_date().strftime('%Y-%m-%d')
            execute_query("UPDATE groceries SET item=?, quantity=?, expiration_date=? WHERE id=?", item, quantity,
                          expiration_date, selected_tuple[0])
            selected_tuple = (selected_tuple[0], item, quantity, selected_tuple[3], expiration_date)
            update_view()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while updating the grocery: {e}")
    else:
        messagebox.showerror("Error", "Please select a row to update.")


def delete_grocery(id):
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute("DELETE FROM groceries WHERE id=?", (id,))
    conn.commit()
    conn.close()


def delete_command():
    global selected_tuple
    if selected_tuple:
        delete_grocery(selected_tuple[0])
        update_view()
    else:
        messagebox.showerror


def select_row(event):
    global selected_tuple
    try:
        item = grocery_tree.item(grocery_tree.selection())['values']
        expiration_date = cal.get_date().strftime('%Y-%m-%d')
        selected_tuple = (item[0], item[1], item[2], item[3], expiration_date)
        item_text.set(item[1])
        quantity_text.set(item[2])
    except IndexError:
        pass


# sets text fields to empty boxes
def update_view():
    item_text.set("")
    quantity_text.set("")
    cal.set_date(datetime.today())
    update_treeview()


# GUI setup
root = tk.Tk()
root.title("Fridge Management")

# Set the color palette
color1 = "#7DB9B6"
color2 = "#E96479"
color3 = "#F5E9CF"
color4 = "#4D455D"

# Setting up the app's title and background color
root.title("Fridge Management")
root.configure(bg=color3)

# Make the app full size
root.state('zoomed')

# Setting up the label for the item and quantity text
item_text = tk.StringVar()
e1 = ttk.Entry(root, textvariable=item_text, font=("Arial", 14))
e1.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)

# Use a Combobox for quantity selection
quantity_text = tk.StringVar()
quantity_options = list(range(1, 21))
e2 = ttk.Combobox(root, textvariable=quantity_text, values=quantity_options, state="readonly", font=("Arial", 14))
e2.grid(row=0, column=3, sticky=tk.W, pady=10, padx=10)
e2.set(quantity_options[0])

# Setting up the label for the expiration date text


cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, year=2022)
cal.grid(row=4, column=3, sticky=tk.W, padx=20, pady=10)

ttk.Label(root, text="Item", background=color3, foreground=color4, font=('Arial Bold', 15)).grid(row=0, column=0,
                                                                                                 padx=20, pady=10)
item_text = tk.StringVar()
e1 = ttk.Entry(root, textvariable=item_text, font=("Arial", 14))
e1.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)

ttk.Label(root, text="Quantity", background=color3, foreground=color4, font=('Arial Bold', 15)).grid(row=0, column=2,
                                                                                                     padx=20, pady=10)

ttk.Label(root, text="Expiration Date", background=color3, foreground=color4, font=('Arial Bold', 15)).grid(row=1,
                                                                                                            column=0,
                                                                                                            padx=20,
                                                                                                            pady=10)

grocery_tree = ttk.Treeview(root)
grocery_tree.grid(row=2, column=0, rowspan=6, columnspan=2, sticky=tk.NSEW, pady=10, padx=20)
sb1 = ttk.Scrollbar(root, orient="vertical", command=grocery_tree.yview)
sb1.grid(row=2, column=2, rowspan=6, sticky=tk.NS, pady=10)

grocery_tree.configure(yscrollcommand=sb1.set)

# Define columns for the treeview and set their headings
grocery_tree["columns"] = ("id", "item", "quantity", "date_added", "expiration_date")
grocery_tree.heading("id", text="ID")
grocery_tree.heading("item", text="Item")
grocery_tree.heading("quantity", text="Quantity")
grocery_tree.heading("date_added", text="Date Added")
grocery_tree.heading("expiration_date", text="Expiration Date")

add_button = ttk.Button(root, text="Add", command=add_command)
add_button.grid(row=8, column=0, pady=10, padx=10)

update_button = ttk.Button(root, text="Update", command=update_command, state="disabled")
delete_button = ttk.Button(root, text="Delete", command=delete_command, state="disabled")
update_button.grid(row=8, column=1, pady=10, padx=10)
delete_button.grid(row=8, column=2, pady=10, padx=10)


def on_select(event):
    global selected_tuple
    selected_item = grocery_tree.focus()
    if selected_item:
        selected_tuple = grocery_tree.item(selected_item)['values']
        update_button.config(state="normal")
        delete_button.config(state="normal")
    else:
        selected_tuple = None
        update_button.config(state="disabled")
        delete_button.config(state="disabled")


grocery_tree.bind("<<TreeviewSelect>>", on_select)

# Set column width
grocery_tree.column("id", width=50, anchor="center")
grocery_tree.column("item", width=150)
grocery_tree.column("quantity", width=100, anchor="center")
grocery_tree.column("date_added", width=150)
grocery_tree.column("expiration_date", width=150)

# Bind a function to the double-click event to select a row
grocery_tree.bind("<Double-1>", select_row)

# Populate the treeview with data from the database
update_treeview()
root.mainloop()
