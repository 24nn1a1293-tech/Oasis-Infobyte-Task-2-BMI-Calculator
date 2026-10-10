import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


# Database connection
def connect_database():
    try:
        conn = sqlite3.connect("bmi_records.db")

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        conn.commit()
        return conn

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not connect to database:\n{error}"
        )
        return None


# Calculate BMI category
def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


# Calculate BMI
def calculate_bmi():
    username = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()

    # Validate empty fields
    if not username or not weight_text or not height_text:
        messagebox.showerror(
            "Input Error",
            "Please fill in all fields."
        )
        return

    # Validate numeric inputs
    try:
        weight = float(weight_text)
        height = float(height_text)

    except ValueError:
        messagebox.showerror(
            "Input Error",
            "Weight and height must be numeric values."
        )
        return

    # Validate positive values
    if weight <= 0 or height <= 0:
        messagebox.showerror(
            "Input Error",
            "Weight and height must be greater than zero."
        )
        return

    # Calculate BMI
    bmi = weight / (height ** 2)

    # Determine category
    category = get_category(bmi)

    # Set result color
    if category == "Normal":
        color = "green"
    elif category == "Underweight":
        color = "orange"
    else:
        color = "red"

    # Display result
    result_label.config(
        text=f"BMI: {bmi:.2f}\nCategory: {category}",
        fg=color
    )

    # Save record
    save_record(username, weight, height, bmi, category)


# Save BMI record
def save_record(username, weight, height, bmi, category):
    conn = None

    try:
        conn = connect_database()

        if conn is None:
            return

        cursor = conn.cursor()

        current_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO bmi_records
            (username, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            weight,
            height,
            bmi,
            category,
            current_date
        ))

        conn.commit()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not save BMI record:\n{error}"
        )

    finally:
        if conn is not None:
            conn.close()


# Display BMI history
def view_history():
    username = name_entry.get().strip()

    if not username:
        messagebox.showerror(
            "Input Error",
            "Please enter a username first."
        )
        return

    conn = None

    try:
        conn = connect_database()

        if conn is None:
            return

        cursor = conn.cursor()

        cursor.execute("""
            SELECT weight, height, bmi, category, date
            FROM bmi_records
            WHERE username = ?
            ORDER BY id DESC
        """, (username,))

        records = cursor.fetchall()

        if not records:
            messagebox.showinfo(
                "History",
                "No BMI records found for this user."
            )
            return

        history_window = tk.Toplevel(root)
        history_window.title(f"{username}'s BMI History")
        history_window.geometry("650x350")

        history_text = tk.Text(
            history_window,
            width=75,
            height=18
        )

        history_text.pack(padx=10, pady=10)

        history_text.insert(
            tk.END,
            f"BMI HISTORY FOR {username}\n\n"
        )

        for record in records:
            weight, height, bmi, category, date = record

            history_text.insert(
                tk.END,
                f"Date: {date} | "
                f"Weight: {weight} kg | "
                f"Height: {height} m | "
                f"BMI: {bmi:.2f} | "
                f"Category: {category}\n\n"
            )

        history_text.config(state=tk.DISABLED)

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not retrieve history:\n{error}"
        )

    finally:
        if conn is not None:
            conn.close()


# Display BMI trend graph
def show_graph():
    username = name_entry.get().strip()

    if not username:
        messagebox.showerror(
            "Input Error",
            "Please enter a username first."
        )
        return

    conn = None

    try:
        conn = connect_database()

        if conn is None:
            return

        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, bmi
            FROM bmi_records
            WHERE username = ?
            ORDER BY id
        """, (username,))

        records = cursor.fetchall()

        if not records:
            messagebox.showinfo(
                "Graph",
                "No BMI records available for this user."
            )
            return

        dates = [record[0] for record in records]
        bmi_values = [record[1] for record in records]

        plt.figure(figsize=(9, 5))

        plt.plot(
            range(1, len(bmi_values) + 1),
            bmi_values,
            marker="o",
            label="BMI"
        )

        plt.xticks(
            range(1, len(dates) + 1),
            dates,
            rotation=45,
            ha="right"
        )

        plt.axhline(
            y=18.5,
            linestyle="--",
            label="BMI 18.5"
        )

        plt.axhline(
            y=25,
            linestyle="--",
            label="BMI 25"
        )

        plt.axhline(
            y=30,
            linestyle="--",
            label="BMI 30"
        )

        plt.title(f"BMI Trend for {username}")
        plt.xlabel("Record Date")
        plt.ylabel("BMI")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not retrieve graph data:\n{error}"
        )

    except Exception as error:
        messagebox.showerror(
            "Graph Error",
            f"Could not display graph:\n{error}"
        )

    finally:
        if conn is not None:
            conn.close()


# Create GUI
root = tk.Tk()

root.title("BMI Calculator")
root.geometry("450x500")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="BMI CALCULATOR",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=20)


# Username
name_label = tk.Label(
    root,
    text="Enter Username:",
    font=("Arial", 12)
)
name_label.pack()

name_entry = tk.Entry(
    root,
    font=("Arial", 12),
    width=25
)
name_entry.pack(pady=5)


# Weight
weight_label = tk.Label(
    root,
    text="Weight (kg):",
    font=("Arial", 12)
)
weight_label.pack()

weight_entry = tk.Entry(
    root,
    font=("Arial", 12),
    width=25
)
weight_entry.pack(pady=5)


# Height
height_label = tk.Label(
    root,
    text="Height (m):",
    font=("Arial", 12)
)
height_label.pack()

height_entry = tk.Entry(
    root,
    font=("Arial", 12),
    width=25
)
height_entry.pack(pady=5)


# Calculate button
calculate_button = tk.Button(
    root,
    text="Calculate BMI",
    font=("Arial", 12, "bold"),
    command=calculate_bmi
)
calculate_button.pack(pady=12)


# Result
result_label = tk.Label(
    root,
    text="Enter your details to calculate BMI",
    font=("Arial", 13, "bold"),
    wraplength=400
)
result_label.pack(pady=10)


# History button
history_button = tk.Button(
    root,
    text="View BMI History",
    font=("Arial", 11),
    command=view_history
)
history_button.pack(pady=5)


# Graph button
graph_button = tk.Button(
    root,
    text="View BMI Trend Graph",
    font=("Arial", 11),
    command=show_graph
)
graph_button.pack(pady=5)


# Initialize database
initial_connection = connect_database()

if initial_connection is not None:
    initial_connection.close()


# Run application
root.mainloop()