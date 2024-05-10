import sqlite3
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
from tkinter import font
import datetime

conn = sqlite3.connect("inventory.sqlite")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                  VIN TEXT PRIMARY KEY, 
                  Mileage TEXT,
                  Price TEXT,
                  Model TEXT,
                  Year TEXT,
                  Drivetrain TEXT,
                  Availability TEXT
                  )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        ssn TEXT PRIMARY KEY,
        name TEXT,
        address TEXT,    -- Add this line to create the address column
        city TEXT,
        state TEXT,
        ZIP TEXT
    )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
    invoice_number TEXT PRIMARY KEY,
    name TEXT,
    VIN TEXT,
    price TEXT,
    paymentType TEXT,
    date TEXT,
    FOREIGN KEY (VIN) REFERENCES vehicles (VIN)
    FOREIGN KEY (price) REFERENCES vehicles (Price)

)''')
conn.commit()


def insert_new_vehicle(vehicle_data):
    cursor.execute(
        '''INSERT INTO vehicles (VIN, Mileage, Price, Model,Year, Drivetrain, Availability) VALUES (?,?,?,?,?,?,?)''',
        vehicle_data)
    conn.commit()


def update_customer(ssn, name, address, city, state, ZIP):
    cursor.execute("UPDATE customers SET name=?, address=?,city=?, state=?, ZIP=? WHERE ssn=?",
                   (name, city, address, state, ZIP, ssn))
    conn.commit()


def get_all_customers():
    cursor.execute("SELECT * FROM customers")
    return cursor.fetchall()


def get_customer(ssn):
    cursor.execute("SELECT * FROM customers WHERE ssn=?", (ssn,))
    return cursor.fetchone()


def create_customer(ssn, name, address, city, state, ZIP):
    cursor.execute(
        "INSERT INTO customers (ssn, name,address, city, state, ZIP) VALUES (?, ?, ?, ?, ?, ?)",
        (ssn, name, address, city, state, ZIP))
    conn.commit()


def create_invoice(invoice_data):
    cursor.execute('''INSERT INTO invoices (invoice_number, name, VIN, price, paymentType, date) VALUES (?,?,?,?,
    ?,?)''',
                   invoice_data)
    conn.commit()


def delete_vehicle(vin):
    cursor.execute('''DELETE FROM vehicles WHERE VIN = ?''', (vin,))
    conn.commit()


def search_vehicles(field, value):
    cursor.execute(f'''SELECT * FROM vehicles WHERE {field} = ?''', (value,))
    return cursor.fetchall()


def update_vehicle(vin, mileage, price, model, year, drivetrain, availability):
    cursor.execute(
        '''UPDATE vehicles SET Mileage=?, Price=?, Model=?, Year=?, Drivetrain=?, Availability=? WHERE VIN=?''',
        (mileage, price, model, year, drivetrain, availability, vin))
    conn.commit()


def get_all_vehicles():
    cursor.execute('''SELECT * FROM vehicles''')
    return cursor.fetchall()


def get_all_invoices():
    cursor.execute('''SELECT * FROM invoices''')
    return cursor.fetchall()


def get_vehicle(vin):
    cursor.execute("SELECT * FROM vehicles WHERE VIN=?", (vin,))
    return cursor.fetchone()


def get_invoice(invoice_number):
    cursor.execute("SELECT * FROM invoices WHERE invoice_number=?", (invoice_number,))
    return cursor.fetchone()


def update_invoice(invoice_number, name, VIN, price, paymentType, date):
    cursor.execute(
        '''UPDATE invoices SET name=?, VIN=?, price=?, paymentType=?, date=? WHERE invoice_number=?''',
        (name, VIN, price, paymentType, date, invoice_number))
    conn.commit()


def generate_new_vin():
    first_char = random.choice(string.digits)
    second_to_fifth = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
    sixth_char = random.choice(string.digits)
    seventh_char = random.choice(string.digits)
    eighth_to_eleventh = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
    remaining_chars = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(13 - 11 - 1))
    last_5_numbers = ''.join(random.choice(string.digits) for _ in range(5))

    car_VIN = first_char + second_to_fifth + sixth_char + seventh_char + eighth_to_eleventh + remaining_chars + last_5_numbers
    return car_VIN


def generate_invoice_number():
    """Generates a random 5-character invoice number with a letter in the beginning."""
    letters = string.ascii_uppercase
    numbers = string.digits

    # Choose a random letter for the first character
    first_char = random.choice(letters)

    # Choose random digits for the remaining characters
    remaining_chars = ''.join(random.choices(numbers, k=4))

    # Combine the first character and the remaining characters
    invoice_number = first_char + remaining_chars

    return invoice_number


def get_date():
    # Get the current date and time
    current_time = datetime.datetime.now()

    # Extract the current date as a string
    current_date = current_time.date().isoformat()

    return current_date


class InventoryApp(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.search_invoice_treeview = None
        self.right_frame = None
        self.search_treeview = None
        self.vehicle_treeview = None
        self.invoice_results_frame = None
        self.invoice_vars = None
        self.results_frame = None
        self.notebook = None
        self.master = master
        self.customer_frame = None
        self.invoice_frame = None
        self.customer_results_frame = None

        self.mileage_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.drivetrain_var = tk.StringVar()
        self.avail_var = tk.StringVar()
        self.VIN_var = tk.StringVar()

        self.vehicle_vars = {
            "VIN": self.VIN_var,
            "Mileage": self.mileage_var,
            "Price": self.price_var,
            "Model": self.model_var,
            "Year": self.year_var,
            "Drivetrain": self.drivetrain_var,
            "Availability": self.avail_var,
        }

        # self.VIN_options = ["NULL"]
        # self.mileage_options = ["Empty", "0-5,000", "5,000-10,000", "10,000-20,000", "20,000+"]
        # self.price_options = ["Empty", "20,000", "40,000", "50,000", "60,000"]
        self.model_options = ["Empty", "Civic", "Civic Type-R", "Accord", "HR-V", "CR-V", "Pilot", "Passport",
                              "Odyssey", "Ridgeline"]
        self.year_options = ["Empty"] + [str(y) for y in range(2015, 2024)]
        self.drivetrain_options = ["Empty", "FWD", "RWD" "AWD"]
        self.avail_options = ["Empty", "Available", "Unavailable"]

        self.create_widgets()

        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=40)  # Set row height to 30 pixels (default is usually 20)

        self.customer_results_frame = ttk.Frame(self.customer_frame, relief='groove', borderwidth=2)
        self.customer_results_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nesw")
        self.customer_results_frame.columnconfigure(0, weight=1)
        self.customer_results_frame.rowconfigure(0, weight=1)
        # Create the customer treeview
        self.customer_treeview = ttk.Treeview(self.customer_results_frame, show="headings", style="Custom.Treeview")
        self.customer_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")

        # Define columns
        self.customer_treeview['columns'] = ("SSN", "Name", "Address", "City", "State", "ZIP")

        # Format columns
        for col in self.customer_treeview['columns']:
            self.customer_treeview.column(col, width=150, anchor="center")
            self.customer_treeview.heading(col, text=col, anchor="center")
        self.customer_form()

        self.invoice_results_frame = ttk.Frame(self.invoice_frame, relief='groove', borderwidth=2)
        self.invoice_results_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nesw")
        self.invoice_results_frame.columnconfigure(0, weight=1)
        self.invoice_results_frame.rowconfigure(0, weight=1)

        self.invoice_treeview = ttk.Treeview(self.invoice_results_frame, show="headings", style="Custom.Treeview")
        self.invoice_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")
        self.invoice_treeview['columns'] = ("Invoice #", "Name", "VIN", "Price", "Payment Type", "Date")

        for col in self.invoice_treeview['columns']:
            self.invoice_treeview.column(col, width=200, anchor="center")
            self.invoice_treeview.heading(col, text=col, anchor="center")
        self.invoice_form()

    def customer_form(self):
        customer_labels = [
            "SSN", "Name", "Address", "City", "State", "ZIP"
        ]
        self.customer_vars = {}
        for i, label in enumerate(customer_labels):
            ttk.Label(self.customer_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.customer_vars[label] = tk.StringVar()
            ttk.Entry(self.customer_frame, width=40, textvariable=self.customer_vars[label]).grid(row=i, column=0,
                                                                                                  padx=10, pady=5)

        ttk.Button(self.customer_frame, text="Submit", command=self.insert_customer_gui).grid(row=7, column=1, pady=10)
        ttk.Button(self.customer_frame, text="Modify", command=self.modify_customer_gui).grid(row=7, column=0, pady=10)
        ttk.Button(self.customer_frame, text="Delete", command=self.delete_customer_gui).grid(row=7, column=2, pady=10)
        ttk.Button(self.customer_frame, text="Clear", command=self.clear_customer_gui).grid(row=8, column=2, pady=10)
        ttk.Button(self.customer_frame, text="Search", command=self.search_customer_gui).grid(row=8, column=1, pady=10)
        ttk.Button(self.customer_frame, text="Display All", command=self.display_all_customers_gui).grid(row=8,
                                                                                                         column=0,
                                                                                                         pady=10)

    def clear_search_treeview(self):
        if hasattr(self, 'search_treeview'):
            self.search_treeview.delete(*self.search_treeview.get_children())
            self.search_treeview.grid_forget()

    def display_all_customers_gui(self):
        self.clear_search_treeview()

        if self.search_treeview is not None:
            self.search_treeview.delete(*self.search_treeview.get_children())
        if hasattr(self, 'search_treeview'):
            self.search_treeview.delete(*self.search_treeview.get_children())

        # Clear the customer_treeview before adding new data
        self.customer_treeview.delete(*self.customer_treeview.get_children())

        customers = get_all_customers()
        for customer in customers:
            self.customer_treeview.insert("", "end", values=customer)

        def your_copy():
            item = self.customer_treeview.selection()[0]
            ssn = self.customer_treeview.item(item, option='values')[0]
            root.clipboard_clear()
            root.clipboard_append(ssn)

        popup1 = tk.Menu(self.customer_treeview, tearoff=0)
        popup1.add_command(
            command=your_copy,
            label="Copy SSN")

        def popup_menu(event):
            item = self.customer_treeview.identify_row(event.y)
            self.customer_treeview.selection_set(item)
            popup1.post(event.x_root, event.y_root)

        MAC_OS = False
        if sys.platform == 'darwin':
            MAC_OS = True
        if MAC_OS:
            self.customer_treeview.bind('<Button-2>', popup_menu)
        else:
            self.customer_treeview.bind('<Button-3>', popup_menu)

    def search_customer_gui(self):
        ssn = self.customer_vars["SSN"].get()
        name = self.customer_vars["Name"].get()

        search_criteria = {}
        if ssn:
            search_criteria["ssn"] = ssn
        if name:
            search_criteria["name"] = name

        if not search_criteria:
            messagebox.showinfo("Search criteria missing", "Please provide at least one search criteria (Name or SSN).")
            return

        query_parts = [f"{field} = ?" for field in search_criteria]
        query = "SELECT * FROM customers WHERE " + " AND ".join(query_parts)
        values = tuple(search_criteria.values())

        cursor.execute(query, values)
        customers = cursor.fetchall()

        # if hasattr(self, 'search_treeview'):
        #     self.search_treeview.delete(*self.search_treeview.get_children())
        # else:
        self.search_treeview = ttk.Treeview(self.customer_results_frame, show="headings")
        self.search_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")
        # self.customer_treeview = self.search_treeview

        if not customers:
            messagebox.showinfo("No Customers", "No customers found matching the search criteria.")
            self.display_all_customers_gui()
        else:
            # Define columns
            self.search_treeview['columns'] = ("SSN", "Name", "Address", "City", "State", "ZIP")

            # Format columns
            for col in self.search_treeview['columns']:
                self.search_treeview.column(col, width=100, anchor="center")
                self.search_treeview.heading(col, text=col, anchor="center")

            if hasattr(self, 'search_treeview'):
                self.search_treeview.delete(*self.search_treeview.get_children())
            else:
                self.search_treeview = ttk.Treeview(self.customer_results_frame, show="headings")
                self.search_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")

            # Populate search results
            for customer in customers:
                self.search_treeview.insert("", "end", values=customer)

            self.search_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")

        def your_copy():
            item = self.customer_treeview.selection()[0]
            ssn = self.customer_treeview.item(item, option='values')[0]
            root.clipboard_clear()
            root.clipboard_append(ssn)

        popup1 = tk.Menu(self.customer_treeview, tearoff=0)
        popup1.add_command(
            command=your_copy,
            label="Copy SSN")

        def popup_menu(event):
            item = self.customer_treeview.identify_row(event.y)
            self.customer_treeview.selection_set(item)
            popup1.post(event.x_root, event.y_root)

        MAC_OS = False
        if sys.platform == 'darwin':
            MAC_OS = True
        if MAC_OS:
            self.customer_treeview.bind('<Button-2>', popup_menu)
        else:
            self.customer_treeview.bind('<Button-3>', popup_menu)

    def modify_customer_gui(self):
        ssn = self.customer_vars["SSN"].get()
        name = self.customer_vars["Name"].get()
        address = self.customer_vars["Address"].get()
        city = self.customer_vars["City"].get()
        state = self.customer_vars["State"].get()
        ZIP_code = self.customer_vars["ZIP"].get()

        customer = get_customer(ssn)

        if not ssn:
            messagebox.showerror("Error", "SSN is required.")
            return
        if customer:
            # create a list of updated values
            updated_values = []
            if name != "":
                updated_values.append(name)
            else:
                updated_values.append(customer[1])

            if address != "":
                updated_values.append(address)
            else:
                updated_values.append(customer[2])

            if city != "":
                updated_values.append(city)
            else:
                updated_values.append(customer[3])
            if state != "":
                updated_values.append(state)
            else:
                updated_values.append(customer[4])
            if ZIP_code != "":
                updated_values.append(ZIP_code)
            else:
                updated_values.append(customer[5])

            try:
                update_customer(ssn, *updated_values)
                messagebox.showinfo("Success", "Customer updated successfully")
                for var in self.customer_vars.values():
                    var.set("")
                self.display_all_customers_gui()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error updating customer: {e}")
        else:
            messagebox.showerror("Error", "Customer does not exist!")

    def delete_customer_gui(self):
        ssn = self.customer_vars["SSN"].get()

        if not ssn:
            messagebox.showerror("Error", "SSN is required.")
            return
        customer = get_customer(ssn)
        if customer:
            try:
                cursor.execute("DELETE FROM customers WHERE ssn = ?", (ssn,))
                conn.commit()
                messagebox.showinfo("Success", "Customer deleted successfully")
                for var in self.customer_vars.values():
                    var.set("")
                self.display_all_customers_gui()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error deleting customer: {e}")
        else:
            messagebox.showerror("Error", "Customer does not exist!")

    def insert_customer_gui(self):
        ssn = self.customer_vars["SSN"].get()
        name = self.customer_vars["Name"].get()
        address = self.customer_vars["Address"].get()
        city = self.customer_vars["City"].get()
        state = self.customer_vars["State"].get()
        ZIP_code = self.customer_vars["ZIP"].get()

        customer_data = (ssn, name, address, city, state, ZIP_code)
        for i in customer_data:
            if i == "":
                messagebox.showerror("Error", "Fill out all customer information!")
                return
        if customer_data:
            try:
                create_customer(ssn, name, address, city, state, ZIP_code)
                messagebox.showinfo("Success", "Customer added successfully", parent=root)
                for var in self.customer_vars.values():
                    var.set("")
                self.display_all_customers_gui()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error inserting customer: {e}", parent=root)

    def delete_vehicle_gui(self):
        vin = self.vehicle_vars["VIN"].get()
        vehicle = get_vehicle(vin)
        if vin:
            if vehicle:
                try:
                    delete_vehicle(vin)
                    messagebox.showinfo("Success", "Vehicle deleted successfully")
                    self.display_all_vehicles()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error deleting vehicle: {e}")
                finally:
                    new_VIN = generate_new_vin()
                    self.vehicle_vars["VIN"].set(new_VIN)
            else:
                messagebox.showerror("Error", "Vehicle does not exist!")
        else:
            messagebox.showerror("Error", "Please enter a VIN.")

    def clear_customer_gui(self):
        for var in self.customer_vars.values():
            var.set("")
        self.display_all_customers_gui()

    def modify_vehicle_gui(self):
        vin = self.vehicle_vars["VIN"].get()

        if vin:
            # messagebox.showinfo("Your VIN", vin)
            mileage = self.vehicle_vars["Mileage"].get()
            price = self.vehicle_vars["Price"].get()
            model = self.vehicle_vars["Model"].get()
            year = self.vehicle_vars["Year"].get()
            drivetrain = self.vehicle_vars["Drivetrain"].get()
            availability = self.vehicle_vars["Availability"].get()

            # get the existing vehicle data
            vehicle_data = get_vehicle(vin)
            if not vehicle_data:
                messagebox.showerror("Error", "Vehicle not found.")
                return

            # create a list of updated values
            updated_values = []
            if mileage != "Empty" and mileage != "":
                updated_values.append(mileage)
            else:
                updated_values.append(vehicle_data[1])
            if price != "Empty" and price != "":
                updated_values.append(price)
            else:
                updated_values.append(vehicle_data[2])
            if model != "Empty":
                updated_values.append(model)
            else:
                updated_values.append(vehicle_data[3])
            if year != "Empty":
                updated_values.append(year)
            else:
                updated_values.append(vehicle_data[4])
            if drivetrain != "Empty":
                updated_values.append(drivetrain)
            else:
                updated_values.append(vehicle_data[5])
            if availability != "Empty":
                updated_values.append(availability)
            else:
                updated_values.append(vehicle_data[6])

            try:
                messagebox.showinfo("INFO", updated_values)
                update_vehicle(vin, *updated_values)
                messagebox.showinfo("Success", "Vehicle updated successfully.")
                self.display_all_vehicles()
            except Exception as e:
                messagebox.showerror("Error", "Failed to update vehicle: " + str(e))
            finally:
                for var in self.vehicle_vars.values():
                    var.set("Empty")
                new_VIN = generate_new_vin()
                self.vehicle_vars["VIN"].set(new_VIN)
        else:
            messagebox.showerror("Error", "Please enter a VIN.")

    def insert_vehicle(self):

        vehicle_data = tuple(self.vehicle_vars[label].get() for label in self.vehicle_vars)
        new_VIN = generate_new_vin()

        if self.vehicle_vars["VIN"].get():
            try:
                insert_new_vehicle(vehicle_data)

                messagebox.showinfo("Success", "Vehicle added successfully")
                self.display_all_vehicles()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error inserting vehicle: {e}")
            finally:
                for var in self.vehicle_vars.values():
                    var.set("Empty")
                self.vehicle_vars["VIN"].set(new_VIN)
        else:
            messagebox.showerror("Error", "Please enter a VIN #!")

    def display_all_vehicles(self):
        vehicles = get_all_vehicles()
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not vehicles:
            messagebox.showinfo("No Vehicles", "No vehicles found in the database")
        else:
            headers = ["VIN", "Mileage", "Price", "Model", "Year", "Drivetrain", "Availability"]

            # Create a custom style
            style = ttk.Style()
            style.configure("Custom.Treeview", rowheight=50)  # Set row height to 30 pixels (default is usually 20)

            # Create TreeView widget
            tree = ttk.Treeview(self.results_frame, columns=headers, show="headings", style="Custom.Treeview")
            tree.grid(row=0, column=0, padx=5, pady=5)

            # Configure column widths and headings
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, width=110, anchor="center")

            # Insert data into TreeView
            for vehicle in vehicles:
                tree.insert('', tk.END, values=vehicle)

            # Add a scrollbar
            scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=tree.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            tree.configure(yscrollcommand=scrollbar.set)

            def your_copy():
                item = tree.selection()[0]
                vin = tree.item(item, option='values')[0]
                root.clipboard_clear()
                root.clipboard_append(vin)

            popup1 = tk.Menu(tree, tearoff=0)
            popup1.add_command(
                command=your_copy,
                label="Copy VIN")

            def popup_menu(event):
                item = tree.identify_row(event.y)
                tree.selection_set(item)
                popup1.post(event.x_root, event.y_root)

            MAC_OS = False
            if sys.platform == 'darwin':
                MAC_OS = True
            if MAC_OS:
                tree.bind('<Button-2>', popup_menu)
            else:
                tree.bind('<Button-3>', popup_menu)
                # tree.bind('<Button-3>', popup_menu)
        new_VIN = generate_new_vin()
        self.vehicle_vars["VIN"].set(new_VIN)

    def search_vehicles_gui(self):
        search_criteria = {}
        for label, var in self.vehicle_vars.items():
            value = var.get()
            if value and value != "Empty":
                search_criteria[label] = value

        if not search_criteria:
            messagebox.showinfo("Search criteria missing", "Please select at least one search criteria.")
            return

        query_parts = [f"{field} = ?" for field in search_criteria]
        query = "SELECT * FROM vehicles WHERE " + " AND ".join(query_parts)
        values = tuple(search_criteria.values())

        cursor.execute(query, values)
        vehicles = cursor.fetchall()

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not vehicles:
            messagebox.showinfo("No Vehicles", "No vehicles found matching the search criteria.")
        else:
            headers = ["VIN", "Mileage", "Price", "Model", "Year", "Drivetrain", "Availability"]

            # Create a custom style
            style = ttk.Style()
            style.configure("Custom.Treeview", rowheight=50)  # Set row height to 30 pixels (default is usually 20)

            # Create TreeView widget
            tree = ttk.Treeview(self.results_frame, columns=headers, show="headings", style="Custom.Treeview")
            tree.grid(row=0, column=0, padx=5, pady=5)

            # Configure column widths and headings
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, width=100, anchor="center")

            # Insert data into TreeView
            for vehicle in vehicles:
                tree.insert('', tk.END, values=vehicle)

            # Add a scrollbar
            scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=tree.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            tree.configure(yscrollcommand=scrollbar.set)

            def your_copy():
                item = tree.selection()[0]
                vin = tree.item(item, option='values')[0]
                root.clipboard_clear()
                root.clipboard_append(vin)
                # item = tree.selection()[0]
                # messagebox.showinfo("Selected Item", f"You have selected item {item}")
                # root.clipboard_clear()
                # root.clipboard_append(tree.item(item, option='text'))

            popup1 = tk.Menu(tree, tearoff=0)
            popup1.add_command(
                command=your_copy,
                label="Copy VIN")

            def popup_menu(event):
                item = tree.identify_row(event.y)
                tree.selection_set(item)
                popup1.post(event.x_root, event.y_root)

            MAC_OS = False
            if sys.platform == 'darwin':
                MAC_OS = True
            if MAC_OS:
                tree.bind('<Button-2>', popup_menu)
            else:
                tree.bind('<Button-3>', popup_menu)
            # tree.bind('<Button-3>', popup_menu)

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True, fill="both")

        self.vehicle_frame = ttk.Frame(self.notebook)
        self.invoice_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.vehicle_frame, text="Vehicles")
        self.notebook.add(self.invoice_frame, text="Invoices")
        self.customer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customer_frame, text="Customers")

        self.right_frame = ttk.Frame(self.vehicle_frame)
        # self.right_frame.grid(row=0, column=3, rowspan=10, padx=20)
        self.right_frame.grid(column=3, row=1, rowspan=10, padx=10, sticky="ne")
        self.vehicle_frame.columnconfigure(4, weight=1)  # Make the right frame expand horizontally
        self.vehicle_frame.rowconfigure(9, weight=1)  # Make the results frame expand vertically

        self.search_treeview = ttk.Treeview(self.customer_results_frame, show="headings")

        self.vehicle_form()
        self.invoice_form()
        self.customer_form()

    def vehicle_form(self):
        vehicle_labels = [
            "VIN", "Mileage", "Price", "Model", "Year", "Drivetrain", "Availability"
        ]

        self.vehicle_vars = {}
        for i, label in enumerate(vehicle_labels):
            ttk.Label(self.vehicle_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.vehicle_vars[label] = tk.StringVar()

            car_VIN = generate_new_vin()
            if label == "VIN":
                vin_entry = ttk.Entry(self.vehicle_frame, width=20, textvariable=self.vehicle_vars[label])
                vin_entry.insert(0, car_VIN)
                vin_entry.grid(row=i, column=1, padx=10, pady=5)
            elif label == "Mileage":
                mile_entry = ttk.Entry(self.vehicle_frame, width=20, textvariable=self.vehicle_vars[label])
                mile_entry.grid(row=i, column=1, padx=10, pady=5)
            elif label == "Price":
                price_entry = ttk.Entry(self.vehicle_frame, width=20, textvariable=self.vehicle_vars[label])
                price_entry.grid(row=i, column=1, padx=10, pady=5)
            else:
                if label == "Model":
                    options = ["Empty", "Civic", "Civic Type-R", "Accord", "HR-V", "CR-V", "Pilot", "Passport",
                               "Odyssey", "Ridgeline"]
                elif label == "Year":
                    options = ["Empty", ] + [str(year) for year in range(2015, 2024)]
                elif label == "Drivetrain":
                    options = ["Empty", "FWD", "RWD", "AWD"]
                elif label == "Availability":
                    options = ["Empty", "Available", "Unavailable"]
                dropdown = ttk.OptionMenu(self.vehicle_frame, self.vehicle_vars[label], options[0], *options)
                dropdown.grid(row=i, column=1, padx=10, pady=5)

        ttk.Button(self.vehicle_frame, text="Add", command=self.insert_vehicle).grid(row=8, column=0, pady=5)
        ttk.Button(self.vehicle_frame, text="Display All", command=self.display_all_vehicles).grid(row=8, column=1,
                                                                                                   pady=5)
        ttk.Button(self.vehicle_frame, text="Search", command=self.search_vehicles_gui).grid(row=7, column=2, pady=5)

        ttk.Button(self.vehicle_frame, text="Delete", command=self.delete_vehicle_gui).grid(row=7, column=0, pady=10)
        # ttk.Button(self.vehicle_frame, text="Modify", command=self.modify_vehicle_gui).grid(row=7, column=1, pady=10)
        ttk.Button(self.vehicle_frame, text="Modify", command=lambda: self.modify_vehicle_gui()).grid(row=7, column=1,
                                                                                                      pady=10)
        ttk.Button(self.vehicle_frame, text="Purchase", command=self.purchase_vehicle_gui).grid(row=8, column=2,
                                                                                                columnspan=1, pady=10)

        self.results_frame = ttk.Frame(self.right_frame)
        self.results_frame.grid(column=0, row=0, sticky="ne", pady=(0, 0))  # Set pady to (0, 0) and sticky to "n"

        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)

        self.vehicle_treeview = ttk.Treeview(self.results_frame, show="headings")
        self.vehicle_treeview.grid(row=0, column=0, padx=5, pady=5)
        # Define columns
        self.vehicle_treeview['columns'] = ("VIN", "Mileage", "Price", "Model", "Year", "Drivetrain", "Availability")

        # Format columns
        for col in self.vehicle_treeview['columns']:
            self.vehicle_treeview.column(col, width=100, anchor="center")
            self.vehicle_treeview.heading(col, text=col, anchor="center")

    def clear_invoice_search_treeview(self):
        if hasattr(self, 'search_invoice_treeview') and self.search_invoice_treeview is not None:
            self.search_invoice_treeview.delete(*self.search_invoice_treeview.get_children())
            self.search_invoice_treeview = None

    def insert_invoice_gui(self, ssn, name, vin, price, paymentType, date):
        self.clear_invoice_search_treeview()
        vehicle = get_vehicle(vin)
        customer = get_customer(ssn)
        if not vehicle:
            messagebox.showerror("Vehicle not found", f"No vehicle found with ID {vin}")
            return
        if not customer:
            messagebox.showerror("Customer not found", f"No customer found with SSN {ssn}")
            messagebox.showinfo("Help", "Make sure you've registered in the customer tab!")
            return
        # price = vehicle[2]
        invoice_num = generate_invoice_number()
        invoice_data = (invoice_num, name, vin, price, paymentType, str(date))
        availability = "Unavailable"

        # messagebox.showinfo("Invoice Data", invoice_data)
        try:
            create_invoice(invoice_data)
            messagebox.showinfo("Success", "Invoice added successfully", parent=root)
            update_vehicle(vin, vehicle[1], vehicle[2], vehicle[3], vehicle[4], vehicle[5], availability)
            self.display_all_vehicles()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error inserting invoice: {e}", parent=root)

    def purchase_vehicle_gui(self):
        vin = self.vehicle_vars["VIN"].get()
        vehicle = get_vehicle(vin)

        # price = str(vehicle[2]).replace(",", "")

        if not vehicle:
            messagebox.showerror("Vehicle not found", f"No vehicle found with ID {vin}")
            return
        if vehicle[6] == 'Unavailable':
            messagebox.showerror("Vehicle not available", f"The vehicle with ID {vin} is not available for purchase.")
            return

        price = vehicle[2]
        # Open a new window to ask for customer information
        purchase_window = tk.Toplevel(self)
        purchase_window.title("Purchase Vehicle")

        # Make the new window appear on top of the main window
        purchase_window.lift()
        purchase_window.attributes('-topmost', True)
        purchase_window.attributes('-topmost', False)

        ttk.Label(purchase_window, text="Please enter customer information:").grid(row=0, column=0, columnspan=2,
                                                                                   padx=10, pady=10)

        ttk.Label(purchase_window, text="SSN:").grid(row=1, column=0, padx=10, pady=5)
        ssn_var = tk.StringVar()
        ttk.Entry(purchase_window, width=40, textvariable=ssn_var).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(purchase_window, text="Name:").grid(row=2, column=0, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(purchase_window, width=40, textvariable=name_var).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(purchase_window, text="Payment Method:").grid(row=3, column=0, padx=10, pady=5)
        paymentType_var = tk.StringVar()
        ttk.Entry(purchase_window, width=40, textvariable=paymentType_var).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(purchase_window, text="Date:").grid(row=4, column=0, padx=10, pady=5)
        date_var = tk.StringVar()
        date_var.set(get_date())
        ttk.Entry(purchase_window, width=40, textvariable=date_var).grid(row=4, column=1, padx=10, pady=5)

        ttk.Button(purchase_window, text=" Confirm",
                   command=lambda: (
                       self.insert_invoice_gui(ssn_var.get(), name_var.get(), vin, price, paymentType_var.get(),
                                               date_var.get()),
                       purchase_window.destroy())).grid(row=5, column=1, pady=10)

        purchase_window.mainloop()

    def invoice_form(self):
        invoice_labels = [
            "Invoice Number", "Name", "VIN", "Price", "Payment Type", "Date"
        ]
        self.invoice_vars = {}
        for i, label in enumerate(invoice_labels):
            ttk.Label(self.invoice_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.invoice_vars[label] = tk.StringVar()
            ttk.Entry(self.invoice_frame, width=40, textvariable=self.invoice_vars[label]).grid(row=i, column=0,
                                                                                                padx=10, pady=5)

        ttk.Button(self.invoice_frame, text="Modify", command=self.modify_invoice_gui).grid(row=6, column=0, pady=10)
        ttk.Button(self.invoice_frame, text="Delete", command=self.delete_invoice_gui).grid(row=6, column=1, pady=10)
        ttk.Button(self.invoice_frame, text="Search", command=self.search_invoice_gui).grid(row=7, column=1, pady=10)
        ttk.Button(self.invoice_frame, text="Display All", command=self.display_all_invoices_gui).grid(row=7, column=0,
                                                                                                       pady=10)

    def display_all_invoices_gui(self):
        self.invoice_treeview.delete(*self.invoice_treeview.get_children())
        if hasattr(self, 'search_invoice_treeview') and self.search_invoice_treeview is not None:
            self.search_invoice_treeview.delete(*self.search_invoice_treeview.get_children())
            self.search_invoice_treeview.grid_forget()
            del self.search_invoice_treeview

        # Replace 'get_all_invoices' with the actual function that retrieves all invoices from the database
        invoices = get_all_invoices()
        for invoice in invoices:
            self.invoice_treeview.insert("", "end", values=invoice)

        def your_copy():
            item = self.invoice_treeview.selection()[0]
            invoice_number = self.invoice_treeview.item(item, option='values')[0]
            root.clipboard_clear()
            root.clipboard_append(invoice_number)

        popup1 = tk.Menu(self.invoice_treeview, tearoff=0)
        popup1.add_command(
            command=your_copy,
            label="Copy Invoice Number")

        def popup_menu(event):
            item = self.invoice_treeview.identify_row(event.y)
            self.invoice_treeview.selection_set(item)
            popup1.post(event.x_root, event.y_root)

        MAC_OS = False
        if sys.platform == 'darwin':
            MAC_OS = True
        if MAC_OS:
            self.invoice_treeview.bind('<Button-2>', popup_menu)
        else:
            self.invoice_treeview.bind('<Button-3>', popup_menu)

    def modify_invoice_gui(self):
        invoice_number = self.invoice_vars["Invoice Number"].get()
        name = self.invoice_vars["Name"].get()
        vin = self.invoice_vars["VIN"].get()
        price = self.invoice_vars["Price"].get()
        payment_type = self.invoice_vars["Payment Type"].get()
        date = self.invoice_vars["Date"].get()

        invoice_data = get_invoice(invoice_number)
        if invoice_data:
            # create a list of updated values
            updated_values = []
            if name != "":
                updated_values.append(name)
            else:
                updated_values.append(invoice_data[1])

            if vin != "":
                updated_values.append(vin)
            else:
                updated_values.append(invoice_data[2])

            if price != "":
                updated_values.append(price)
            else:
                updated_values.append(invoice_data[3])
            if payment_type != "":
                updated_values.append(payment_type)
            else:
                updated_values.append(invoice_data[4])
            if date != "":
                updated_values.append(date)
            else:
                updated_values.append(invoice_data[5])

            if not invoice_number:
                messagebox.showerror("Error", "Invoice Number is required.")
                return

            try:
                update_invoice(invoice_number, *updated_values)
                messagebox.showinfo("Success", "Invoice updated successfully")
                self.display_all_invoices_gui()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error updating invoice: {e}")
        else:
            messagebox.showerror("Error", "Invoice # does not exist!")

    def delete_invoice_gui(self):
        invoice_number = self.invoice_vars["Invoice Number"].get()
        invoice = get_invoice(invoice_number)

        if not invoice_number:
            messagebox.showerror("Error", "Invoice Number is required.")
            return
        if invoice:
            try:
                cursor.execute("DELETE FROM invoices WHERE invoice_number = ?", (invoice_number,))
                conn.commit()
                messagebox.showinfo("Success", "Invoice deleted successfully")
                self.display_all_invoices_gui()
                for var in self.invoice_vars.values():
                    var.set("")
                self.display_all_customers_gui()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error deleting invoice: {e}")
        else:
            messagebox.showerror("Error", "Invoice does not exist!")

    def search_invoice_gui(self):
        invoice_number = self.invoice_vars["Invoice Number"].get()
        name = self.invoice_vars["Name"].get()
        vin = self.invoice_vars["VIN"].get()
        price = self.invoice_vars["Price"].get()
        payment_type = self.invoice_vars["Payment Type"].get()
        date = self.invoice_vars["Date"].get()

        search_criteria = {}
        if invoice_number:
            search_criteria["invoice_number"] = invoice_number
        if name:
            search_criteria["name"] = name
        if vin:
            search_criteria["vin"] = vin
        if price:
            search_criteria["price"] = price
        if payment_type:
            search_criteria["paymentType"] = payment_type
        if date:
            search_criteria["date"] = date

        if not search_criteria:
            messagebox.showinfo("Search criteria missing", "Please provide at least one search criteria.")
            return

        query_parts = [f"{field} = ?" for field in search_criteria]
        query = "SELECT * FROM invoices WHERE " + " AND ".join(query_parts)
        values = tuple(search_criteria.values())

        cursor.execute(query, values)
        invoices = cursor.fetchall()

        self.search_invoice_treeview = ttk.Treeview(self.invoice_results_frame, show="headings")
        self.search_invoice_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")
        # self.invoice_treeview = self.search_treeview

        if not invoices:
            messagebox.showinfo("No Invoices", "No invoices found matching the search criteria.")
            if hasattr(self, 'search_invoice_treeview'):
                self.search_invoice_treeview.delete(*self.search_invoice_treeview.get_children())
                self.search_invoice_treeview.grid_forget()
                del self.search_invoice_treeview
            self.display_all_invoices_gui()
        else:
            # Define columns
            self.search_invoice_treeview['columns'] = ("Invoice #", "Name", "VIN", "Price", "Payment Type", "Date")

            # Format columns
            for col in self.search_invoice_treeview['columns']:
                self.search_invoice_treeview.column(col, width=110, anchor="center")
                self.search_invoice_treeview.heading(col, text=col, anchor="center")

            if hasattr(self, 'search_invoice_treeview'):
                self.search_invoice_treeview.delete(*self.search_invoice_treeview.get_children())
            else:
                self.search_invoice_treeview = ttk.Treeview(self.invoice_results_frame, show="headings")
                self.search_invoice_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")

            # Populate search results
            for invoice in invoices:
                self.search_invoice_treeview.insert("", "end", values=invoice)

            self.search_invoice_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")

            def your_copy():
                item = self.search_invoice_treeview.selection()[0]
                invoice_number = self.search_invoice_treeview.item(item, option='values')[0]
                root.clipboard_clear()
                root.clipboard_append(invoice_number)

            popup1 = tk.Menu(self.search_invoice_treeview, tearoff=0)
            popup1.add_command(
                command=your_copy,
                label="Copy Invoice Number")

            def popup_menu(event):
                item = self.search_invoice_treeview.identify_row(event.y)
                self.search_invoice_treeview.selection_set(item)
                popup1.post(event.x_root, event.y_root)

            MAC_OS = False
            if sys.platform == 'darwin':
                MAC_OS = True
            if MAC_OS:
                self.search_invoice_treeview.bind('<Button-2>', popup_menu)
            else:
                self.search_invoice_treeview.bind('<Button-3>', popup_menu)


if __name__ == "__main__":
    root = tk.Tk()

    default_font = font.nametofont("TkDefaultFont")  # Get the default font
    default_font.configure(size=14)  # Set the default font size to 14

    root.option_add("*Font", default_font)  # Apply the default font to all widgets
    root.title("Honda Dealership #672 Inventory")
    root.geometry("1300x1000")

    app = InventoryApp(root)
    app.pack(expand=True, fill="both")
    app.mainloop()
