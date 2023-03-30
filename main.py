from tkinter import font
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Database setup
def init_db():
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS groceries (id INTEGER PRIMARY KEY, item TEXT, quantity INTEGER)''')
    conn.commit()
    conn.close()


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


def view_groceries():
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute("SELECT * FROM groceries")
    rows = c.fetchall()
    conn.close()
    return rows

def update_grocery(id, item, quantity):
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute("UPDATE groceries SET item=?, quantity=? WHERE id=?", (item, quantity, id))
    conn.commit()
    conn.close()
    display_groceries()

def delete_grocery(id):
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute("DELETE FROM groceries WHERE id=?", (id,))
    conn.commit()
    conn.close()
    display_groceries()

def display_groceries():
    rows = view_groceries()
    grocery_list.delete(0, tk.END)
    for row in rows:
        grocery_list.insert(tk.END, row)

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

    add_grocery(item, quantity)
    item_text.set("")
    quantity_text.set("")
    display_groceries()


def update_command():
    try:
        if selected_tuple:
            update_grocery(selected_tuple[0], item_text.get(), int(quantity_text.get()))
            item_text.set("")
            quantity_text.set("")
            display_groceries()
        else:
            messagebox.showerror("Error", "Please select a row to update.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while updating the grocery: {e}")

def delete_command():
    delete_grocery(selected_tuple[0])

def bind_enter_key(event):
    add_button.invoke() # invoke the add_button command when Enter is pressed

def select_row(event):
    # Get the selected row
    global selected_row
    index = grocery_list.curselection()[0]
    selected_row = grocery_list.get(index)

    # Update the entry fields with the selected row data
    item_entry.delete(0, tk.END)
    item_entry.insert(tk.END, selected_row[1])
    quantity_entry.delete(0, tk.END)
    quantity_entry.insert(tk.END, selected_row[2])

    # Update the update button command to use the selected row id
    update_button.configure(command=lambda: update_command(selected_row[0]))




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
root.bind('<Return>', bind_enter_key) # bind the Enter key to the root window
# Bind the "<Return>" event to the update button
root.bind("<Return>", lambda event: update_button.invoke())

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
ttk.Label(root, text="Quantity", background=color3, foreground=color4, font=('Arial Bold', 15)).grid(row=0, column=2, padx=20, pady=10)

# Adjust Listbox and Scrollbar for full size
grocery_list = tk.Listbox(root, height=20, width=40, font=("Arial", 14))
grocery_list.grid(row=1, column=0, rowspan=6, columnspan=2, sticky=tk.NSEW, pady=10, padx=20)

grocery_list.bind('<<ListboxSelect>>', get_selected_row)

sb1 = ttk.Scrollbar(root)
sb1.grid(row=1, column=2, rowspan=6, sticky=tk.NS, pady=10)

grocery_list.configure(yscrollcommand=sb1.set)
sb1.configure(command=grocery_list.yview)

# # Load the image for the Add button
# add_icon = tk.PhotoImage(file="add.png")

# Buttons

# Creating a custom style for the buttons
style = ttk.Style()

# Setting the button background colors
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
close_button.grid(row=5, column=3, sticky=tk.EW,  pady=(0, 50),  padx=10)


# Create a custom style for buttons
style = ttk.Style()
style.configure('Custom.TButton', background=color4, foreground=color4)

# Configure grid weights for better resizing
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=0)
root.grid_columnconfigure(3, weight=1)
root.grid_rowconfigure(1, weight=1)

init_db()
display_groceries()





root.mainloop()