import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from PIL import Image, ImageTk
from tkinter import StringVar
from tkinter.ttk import OptionMenu



# Database setup
conn = sqlite3.connect('fridge.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS groceries (id INTEGER PRIMARY KEY, item TEXT, quantity INTEGER)''')
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

def update_listbox():
    grocery_list.delete(0, tk.END)
    rows = execute_query("SELECT * FROM groceries")
    for row in rows:
        grocery_list.insert(tk.END, row)

def add_command():
    item = item_text.get()
    quantity = quantity_text.get()

    # Check if item or quantity input is empty or only contains whitespace
    if not item.strip() or not quantity.strip():
        messagebox.showerror("Error", "Please enter a valid item and quantity.")
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
        execute_query("INSERT INTO groceries (item, quantity) VALUES (?, ?)", item, quantity)

    item_text.set("")
    quantity_text.set("")
    update_listbox()


def update_command():
    global selected_tuple
    if selected_tuple:
        try:
            update_grocery(selected_tuple[0], item_text.get(), int(quantity_text.get()))
            item_text.set("")
            quantity_text.set("")
            display_groceries()
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
    else:
        messagebox.showerror("Error", "Please select a row to delete.")

    update_listbox()

def select_row(event):
    try:
        global selected_tuple
        index = grocery_list.curselection()[0]
        selected_tuple = grocery_list.get(index)
        item_text.set(selected_tuple[1])
        quantity_text.set(selected_tuple[2])
    except IndexError:
        pass

selected_tuple = None

def get_selected_row(event):
    try:
        global selected_tuple
        index = grocery_list.curselection()[0]
        selected_tuple = grocery_list.get(index)
        e1.delete(0, tk.END)
        e1.insert(tk.END, selected_tuple[1])
        e2.delete(0, tk.END)
        e2.insert(tk.END, selected_tuple[2])
    except IndexError:
        pass

def add_grocery(item, quantity):
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()

    # Check if item already exists in the database
    c.execute("SELECT * FROM groceries WHERE item=?", (item,))
    existing_item = c.fetchone()

    if existing_item:
        # Item already exists, so update the quantity
        new_quantity = existing_item[2] + int(quantity)
        c.execute("UPDATE groceries SET quantity=? WHERE id=?", (new_quantity, existing_item[0]))
    else:
        # Item does not exist, so add it to the database
        c.execute("INSERT INTO groceries (item, quantity) VALUES (?, ?)", (item, quantity))

    conn.commit()
    conn.close()

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

ttk.Label(root, text="Item", background=color3, foreground=color4, font=('Arial Bold', 15)).grid(row=0, column=0, padx=20, pady=10)
item_text = tk.StringVar()
e1 = ttk.Entry(root, textvariable=item_text, font=("Arial", 14))
e1.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)

ttk.Label(root, text="Quantity", background=color3, foreground=color4, font=('Arial Bold', 15)).grid(row=0, column=2, padx=20, pady=10)
grocery_list = tk.Listbox(root, height=20, width=40, font=("Arial", 14))
grocery_list.grid(row=1, column=0, rowspan=6, columnspan=2, sticky=tk.NSEW, pady=10, padx=20)
sb1 = ttk.Scrollbar(root)
sb1.grid(row=1, column=2, rowspan=6, sticky=tk.NS, pady=10)

grocery_list.configure(yscrollcommand=sb1.set)
sb1.configure(command=grocery_list.yview)
grocery_list.bind('<<ListboxSelect>>', get_selected_row)
style = ttk.Style()

style.map("Custom.TButton",
background=[("pressed", color4), ("active", color4)],
foreground=[("pressed", color4), ("active", color4)])

# Setting the button fonts and sizes
style.configure("Custom.TButton",
font=("Arial", 14),
padding=10,
background=color4,
foreground=color4)

# Buttons
add_button = ttk.Button(root, text="Add", command=add_command, style="Custom.TButton")
add_button.grid(row=2, column=3, sticky=tk.EW, padx=10)

update_button = ttk.Button(root, text="Update", command=update_command, style="Custom.TButton")
update_button.grid(row=3, column=3, sticky=tk.EW, padx=10)

delete_button = ttk.Button(root, text="Delete", command=delete_command, style="Custom.TButton")
delete_button.grid(row=4, column=3, sticky=tk.EW, padx=10)

close_button = ttk.Button(root, text="Close", command=root.destroy, style="Custom.TButton")
close_button.grid(row=5, column=3, sticky=tk.EW, pady=(0, 50), padx=10)

# Set the command to the add_button when Enter is pressed
# root.bind('<Return>', bind_enter_key)

# Set the command to the update_button when Return is pressed
root.bind("<Return>", lambda event: update_button.invoke())

# Custom button style
style = ttk.Style()
style.configure('Custom.TButton', background=color4, foreground=color4)

# Configure grid weights for better resizing
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=0)
root.grid_columnconfigure(3, weight=1)
root.grid_rowconfigure(1, weight=1)


update_listbox()

root.mainloop()
