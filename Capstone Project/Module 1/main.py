# Core Python
import os
import sys
import hashlib
import datetime
from datetime import datetime

# MySQL Connector
import mysql.connector

# Data Analysis
import numpy as np

# App
from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    DataTable,
    Placeholder,
    Label,
    Input,
    Button,
    Select,
    Label,
)
from textual.containers import HorizontalGroup, VerticalScroll
from textual.screen import Screen, ModalScreen


# =========================================  CORE FUNCTIONS  =========================================

mydb = mysql.connector.connect(
    host="localhost", user="root", password="ArhamAlfa123", database="car_rentals"
)
cursor = mydb.cursor()


def login(username, password):
    cursor.execute("SELECT user_name, user_password from users")
    users = cursor.fetchall()
    cursor.execute("SELECT employee_name, employee_password from employees")
    employees = cursor.fetchall()

    # If normal user
    for user in users:
        if username == user[0]:
            if password == user[1]:
                return {True: "user"}  # User exists and password was correct
            else:
                return {False: None}  # User exists but password was incorrect

    # Else if employee
    for employee in employees:
        if username == employee[0]:
            if password == employee[1]:
                return {True: "employee"}  # Employee exists and password was correct
            else:
                return {False: None}  # Employee exists but password was incorrect

    return None  # User does not exist


# ======================== SETTER FUNCTIONS ========================
def addCar(
    car_plate, car_make, car_model, car_category, car_year, car_km, car_fee
) -> tuple:
    command = "INSERT INTO cars (car_plate, car_make, car_model, car_category,car_year, car_km, car_fee) values (%s, %s, %s, %s, %s, %s, %s);"
    values = (car_plate, car_make, car_model, car_category, car_year, car_km, car_fee)
    cursor.execute(command, values)
    mydb.commit()
    return (True, f"{cursor.rowcount} record(s) inserted into cars.")


def addUser(user_name, user_password) -> tuple:
    cursor.execute("SELECT user_name from users;")
    users = cursor.fetchall()
    values = (user_name, user_password)
    # VERIFY
    if user_name in users:
        return (False, "Username already exists.")
    else:
        command = "INSERT INTO users (user_name, user_password) values (%s, %s)"
        cursor.execute(command, values)
        mydb.commit
        return (True, "User has been added.")


def addEmployee(employee_name, employee_password, employee_commission) -> tuple:
    cursor.execute("SELECT employee_name from employees;")
    employees = cursor.fetchall()
    values = (employee_name, employee_password, employee_commission)
    # VERIFY
    if employee_name in employees:
        return (False, "Employee already exists.")
    else:
        command = "INSERT INTO employees (employee_name, employee_password, employee_commission) values (%s, %s, %s);"
        cursor.execute(command, values)
        mydb.commit
        return (True, "User has been added.")


def addRental(renter_id, rentee_id, vehicle_id, rental_start, rental_end) -> tuple:
    format = "%Y-%m-%d"
    try:
        _rental_start = datetime.strptime(rental_start, format)
        _rental_end = datetime.strptime(rental_end, format)
    except ValueError:
        return (False, "Wrong date format.")

    if _rental_start > _rental_end:
        return (False, "Rental end cannot be earlier than rental start.")
    else:
        command = "INSERT INTO rentals (renter_id, rentee_id, vehicle_id, rental_start, rental_end) values (%s, %s, %s, %s, %s);"
        values = (renter_id, rentee_id, vehicle_id, rental_start, rental_end)
        cursor.execute(command, values)
        mydb.commit()
        return (True, "Rental has been added.")


# ======================== GETTER FUNCTIONS ========================
def getCars() -> list[tuple]:
    cursor.execute("SELECT * FROM cars;")
    return cursor.fetchall()


def getUsers() -> list[tuple]:
    cursor.execute("SELECT * FROM users;")
    return cursor.fetchall()


def getEmployees() -> list[tuple]:
    cursor.execute("SELECT * FROM employees;")
    return cursor.fetchall()


def getRentals() -> list[tuple]:
    cursor.execute(
        """SELECT r.rental_id, e.employee_name, u.user_name, c.car_model, c.car_plate, r.rental_start, r.rental_end FROM rentals r
            JOIN employees e ON e.employee_id = r.renter_id
            JOIN users u ON u.user_id = r.rentee_id
            JOIN cars c ON c.car_id = r.vehicle_id
            ORDER BY r.rental_id ASC;"""
    )
    return cursor.fetchall()


# ======================== STATISTIC FUNCTIONS ========================
def getTopEmployees():
    command = """SELECT e.employee_name,
        SUM(datediff(r.rental_end, r.rental_start) * c.car_fee) AS total_revenue
        FROM employees    e
        LEFT JOIN rentals r ON employee_id  = renter_id
        LEFT JOIN cars    c ON r.vehicle_id = car_id
        GROUP BY  e.employee_name
        ORDER BY  total_revenue DESC;
        """
    cursor.execute(command)

    return cursor.fetchall()


def getTopCategory():
    command = """SELECT c.car_category, COUNT(r.vehicle_id) AS total_cars
        FROM cars c
        JOIN rentals r ON c.car_id = r.vehicle_id
        GROUP BY c.car_category
        ORDER BY total_cars DESC;
        """
    cursor.execute(command)

    return cursor.fetchall()


def getTopModel():
    command = """SELECT c.car_make, c.car_model, COUNT(r.vehicle_id) AS total_cars
        FROM cars c
        JOIN rentals r ON c.car_id = r.vehicle_id
        GROUP BY c.car_make, c.car_model
        ORDER BY total_cars DESC;
        """
    cursor.execute(command)

    return cursor.fetchall()


# Utilization rate is (days rented / years owned), and shows how utilized each car is.
def getUtilizationRate():
    command = """SELECT c.car_id, c.car_plate, c.car_make, c.car_model, SUM((datediff(r.rental_end, r.rental_start)) / (YEAR(curdate())  -  c.car_year)) AS utilization_rate
        FROM cars c
        JOIN rentals r ON c.car_id = r.vehicle_id
        GROUP BY c.car_id, c.car_plate, c.car_make, c.car_model
        ORDER BY utilization_rate DESC;
        """
    cursor.execute(command)

    return cursor.fetchall()


def getTopSpender():
    command = """SELECT u.user_name, SUM(datediff(r.rental_end, r.rental_start) * c.car_fee) AS user_spending
        FROM rentals r
        JOIN users u ON r.rentee_id = u.user_id
        JOIN cars c ON r.vehicle_id = c.car_id
        GROUP BY u.user_name
        ORDER BY user_spending DESC;
        """
    cursor.execute(command)

    return cursor.fetchall()


def getTotalRevenue():
    command = """SELECT SUM(datediff(r.rental_end, r.rental_start) * c.car_fee) AS total_revenue
        FROM rentals r
        JOIN cars c ON r.vehicle_id = c.car_id
        """
    cursor.execute(command)

    return cursor.fetchall()


def getAverageRevenue():
    command = """SELECT AVG(datediff(r.rental_end, r.rental_start) * c.car_fee) AS total_revenue
        FROM rentals r
        JOIN cars c ON r.vehicle_id = c.car_id
        """
    cursor.execute(command)

    return cursor.fetchall()


# =========================================  TEXTUAL  =========================================


ROWS = [
    ("Null", "Null"),
    ("Null", "Null"),
    ("Null", "Null"),
    ("Null", "Null"),
    ("Null", "Null"),
    ("Null", "Null"),
]


class Homescreen(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen(CarRentalService())


class CarRentalService(Screen):
    BINDINGS = [
        ("1", "show_employees", "Employees"),
        ("2", "show_users", "Users"),
        ("3", "show_cars", "Cars"),
        ("4", "show_rentals", "Rentals"),
    ]

    CSS_PATH = "D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\car_rental_styling.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield DataTable()
        yield Placeholder("This will be the graph")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    # ========= SCREEN NAVIGATORS =========
    def action_show_employees(self) -> None:
        self.app.push_screen(EmployeesScreen())

    def action_show_users(self) -> None:
        self.app.push_screen(UsersScreen())

    def action_show_cars(self) -> None:
        self.app.push_screen(CarsScreen())

    def action_show_rentals(self) -> None:
        self.app.push_screen(RentalsScreen())


# ======================== SCREENS ========================


class EmployeesScreen(Screen):
    BINDINGS = [
        ("b,escape", "app.pop_screen", "Back"),
        ("a", "add_new", "New"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield DataTable()
        yield Placeholder("This will be the graph")

    def on_mount(self, result=None) -> None:
        table = self.reset_table()
        table.add_columns(
            "Employee ID",
            "Employee Names",
            "Employee Password",
            "Employee Comission Rate",
        )
        table.add_rows(getEmployees())

    def action_add_new(self) -> None:
        self.app.push_screen(AddEmployeeModal(), self.on_mount)

    def reset_table(self) -> DataTable:
        old_table = self.query_one(DataTable)
        parent = old_table.parent
        old_table.remove()

        new_table = DataTable()
        parent.mount(new_table)
        return new_table


class UsersScreen(Screen):
    BINDINGS = [
        ("b,escape", "app.pop_screen", "Back"),
        ("a", "add_new", "New"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield DataTable()
        yield Placeholder("This will be the graph")

    def on_mount(self, result=None) -> None:
        table = self.reset_table()
        table.add_columns(
            "User ID",
            "User Names",
            "User Password",
        )
        table.add_rows(getUsers())

    def action_add_new(self) -> None:
        self.app.push_screen(AddUserModal(), self.on_mount)

    def reset_table(self) -> DataTable:
        old_table = self.query_one(DataTable)
        parent = old_table.parent
        old_table.remove()

        new_table = DataTable()
        parent.mount(new_table)
        return new_table


class CarsScreen(Screen):
    BINDINGS = [
        ("b,escape", "app.pop_screen", "Back"),
        ("a", "add_new", "New Car"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield DataTable()
        yield Placeholder("This will be the graph")

    def on_mount(self, result=None) -> None:
        table = self.reset_table()
        table.add_columns(
            "Car ID",
            "Car Plate",
            "Car Make",
            "Car Model",
            "Car Category",
            "Car Year",
            "Car Km",
            "Car Fee (per day)",
        )
        table.add_rows(getCars())

    def action_add_new(self) -> None:
        self.app.push_screen(AddCarModal(), self.on_mount)

    def reset_table(self) -> DataTable:
        old_table = self.query_one(DataTable)
        parent = old_table.parent
        old_table.remove()

        new_table = DataTable()
        parent.mount(new_table)
        return new_table


class RentalsScreen(Screen):
    BINDINGS = [
        ("b,escape", "app.pop_screen", "Back"),
        ("a", "add_new", "New"),
        ("1", "rev_stats", "Get Revenues"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield DataTable()
        yield Placeholder("This will be the graph")

    def on_mount(self, result=None) -> None:
        table = self.reset_table()
        table.add_columns(
            "Rental ID",
            "Renter Names",
            "Rentee Names",
            "Car Model",
            "Car Plate Number",
            "Rental Start Date",
            "Rental End Date",
        )
        table.add_rows(getRentals())

    def action_add_new(self) -> None:
        self.app.push_screen(AddRentalModal(), self.on_mount)

    def action_rev_stats(self) -> None:
        self.app.push_screen(ShowRevenueStatistics())

    def reset_table(self) -> DataTable:
        old_table = self.query_one(DataTable)
        parent = old_table.parent
        old_table.remove()

        new_table = DataTable()
        parent.mount(new_table)
        return new_table


# ======================== MODAL SCREENS ========================


class AddEmployeeModal(ModalScreen):
    BINDINGS = [
        ("enter", "submit", "Submit"),
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Label("Add Employee", id="title")

        yield Label("Employee Name")
        yield Input(placeholder="e.g., Bob", id="employee_name")

        yield Label("Password")
        yield Input(placeholder="••••••••", id="employee_password", password=True)

        yield Label("Commission Rate")
        yield Input(placeholder="e.g. 0.4", id="employee_commission")

        yield Button("Submit", id="submit", variant="primary")
        yield Button("Cancel", id="cancel")

        yield Label("", id="result")

    def on_mount(self) -> None:
        self.query_one("#employee_name", Input).focus()

    def action_submit(self) -> None:
        vals = (
            self.query_one("#employee_name", Input).value,
            getHash(self.query_one("#employee_password", Input).value),
            self.query_one("#employee_commission", Input).value,
        )

        result = addEmployee(*vals)

        if result[0]:
            self.dismiss()
        else:
            self.query_one("#result", Label).update(result[1])

    def action_cancel(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.action_submit()
        else:
            self.action_cancel()


class AddUserModal(ModalScreen):
    BINDINGS = [
        ("enter", "submit", "Submit"),
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Label("Add User", id="title")

        yield Label("User Name")
        yield Input(placeholder="e.g., alice", id="user_name")

        yield Label("Password")
        yield Input(placeholder="••••••••", id="user_password", password=True)

        yield Button("Submit", id="submit", variant="primary")
        yield Button("Cancel", id="cancel")

        yield Label("", id="result")

    def on_mount(self) -> None:
        self.query_one("#user_name", Input).focus()

    def action_submit(self) -> None:
        vals = (
            self.query_one("#user_name", Input).value,
            getHash(self.query_one("#user_password", Input).value),
        )

        result = addUser(*vals)

        if result[0]:
            self.dismiss()
        else:
            self.query_one("#result", Label).update(result[1])

    def action_cancel(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.action_submit()
        else:
            self.action_cancel()


class AddCarModal(ModalScreen):
    BINDINGS = [
        ("enter", "submit", "Submit"),
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Label("Add Car", id="title")

        yield Label("Car Make")
        yield Input(placeholder="e.g., Toyota", id="car_make")

        yield Label("Car Model")
        yield Input(placeholder="e.g., Corolla", id="car_model")

        yield Label("Category")
        yield Input(
            placeholder="e.g., Budget ~ Rp 400,000 - Rp 600,000 / Family ~ Rp 650,000 - Rp 1,000,000 / Luxury ~ Rp 1,200,000 - Rp 2,000,000",
            id="car_category",
        )

        yield Label("Car Plate")
        yield Input(placeholder="e.g., B 1039 SJW", id="car_plate")

        yield Label("Year")
        yield Input(placeholder="e.g., 2019", id="car_year")

        yield Label("Kilometers")
        yield Input(placeholder="e.g., 45000", id="car_km")

        yield Label("Fee")
        yield Input(placeholder="e.g., 500000", id="car_fee")

        yield Button("Submit", id="submit", variant="primary")
        yield Button("Cancel", id="cancel")

        yield Label("", id="result")

    def on_mount(self) -> None:
        self.query_one("#car_make", Input).focus()

    def action_submit(self) -> None:
        vals = (
            self.query_one("#car_plate", Input).value,
            self.query_one("#car_make", Input).value,
            self.query_one("#car_model", Input).value,
            self.query_one("#car_category", Input).value,
            self.query_one("#car_year", Input).value,
            self.query_one("#car_km", Input).value,
            self.query_one("#car_fee", Input).value,
        )
        result = addCar(*vals)

        if result[0]:
            self.dismiss()
        else:
            self.query_one("#result", Label).update(result[1])

    def action_cancel(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.action_submit()
        else:
            self.action_cancel()


class AddRentalModal(ModalScreen):

    BINDINGS = [("enter", "submit", "Submit"), ("escape", "cancel", "Cancel")]

    def __init__(self):
        super().__init__()
        self._employee_options = [(item[1], item[0]) for item in getEmployees()]
        self._user_options = [(item[1], item[0]) for item in getUsers()]
        self._car_options = [
            (f"{item[2]} {item[3]} ({item[1]})", item[0]) for item in getCars()
        ]

    def compose(self) -> ComposeResult:
        yield Label("Add Rental", id="title")

        yield Label("Renter (Employee)")
        yield Select(options=self._employee_options, id="renter_id")

        yield Label("Rentee ID (customer/user id)")
        yield Select(options=self._user_options, id="rentee_id")

        yield Label("Vehicle ID")
        yield Select(options=self._car_options, id="vehicle_id")

        yield Label("Rental Start")
        yield Input(placeholder="Format: YYYY-MM-DD", id="rental_start")

        yield Label("Rental End")
        yield Input(placeholder="Format: YYYY-MM-DD", id="rental_end")

        yield Button("Submit", id="submit", variant="primary")
        yield Button("Cancel", id="cancel")

        yield Label("", id="result")

    def on_mount(self) -> None:
        self.query_one("#renter_id", Select).focus()

    def action_submit(self) -> None:
        vals = (
            self.query_one("#renter_id", Select).value,
            self.query_one("#rentee_id", Select).value,
            self.query_one("#vehicle_id", Select).value,
            self.query_one("#rental_start", Input).value,
            self.query_one("#rental_end", Input).value,
        )

        result = addRental(*vals)

        if result[0]:
            self.dismiss()
        else:
            self.query_one("#result", Label).update(result[1])

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.action_submit()
        else:
            self.action_cancel()


class ShowRevenueStatistics(ModalScreen):
    BINDINGS = [("enter", "ok", "Ok")]

    def compose(self) -> ComposeResult:
        yield Label(
            f"Total Revenue = Rp {float(getTotalRevenue()[0][0])}", id="total_rev"
        )
        yield Label(
            f"Average Revenue = Rp {float(getAverageRevenue()[0][0])}", id="avg_rev"
        )

        yield Button("OK", id="ok")

    def action_ok(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


# =========================================  HELPER FUNCTIONS  =========================================


def getHash(String) -> str:
    return hashlib.sha256(String.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    app = Homescreen()
    app.run()
