# Core Python
import os
import sys
import hashlib
import datetime

# MySQL Connector
import mysql.connector

# Data Analysis
import numpy as np

# App
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


mydb = mysql.connector.connect(
    host="localhost", user="root", password="ArhamAlfa123", database="car_rentals"
)
cursor = mydb.cursor()

# EXAMPLE FOR HASHING
hashed_password = hashlib.sha256("C8H11No2".encode("utf-8")).hexdigest()


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


# ADDER FUNCTIONS -- Assume all parameters have been validated
def addCar(car_make, car_model, car_category, car_year, car_km, car_fee):
    command = "INSERT INTO cars (car_make, car_model, car_category,car_year, car_km, car_fee) values (%s, %s, %s, %s, %s, %s)"
    values = (car_make, car_model, car_category, car_year, car_km, car_fee)
    cursor.execute(command, values)
    mydb.commit()
    return f"{cursor.rowcount} record(s) inserted into cars."


def addUser(user_name, user_password):
    cursor.execute("SELECT user_name from users")
    users = cursor.fetchall()
    values = (user_name, user_password)
    # VERIFY
    if user_name in users:
        return "Username already exists."
    else:
        command = "INSERT INTO users (user_name, user_password) values (%s, %s)"
        cursor.execute(command, values)
        mydb.commit
        return "User has been added."


def addEmployee(employee_name, employee_password):
    cursor.execute("SELECT employee_name from employees")
    employees = cursor.fetchall()
    values = (employee_name, employee_password)
    # VERIFY
    if employee_name in employees:
        return "Employee already exists."
    else:
        command = (
            "INSERT INTO employees (employee_name, employee_password) values (%s, %s)"
        )
        cursor.execute(command, values)
        mydb.commit
        return "User has been added."


def addRental(renter_id, rentee_id, vehicle_id, rental_start, rental_end):
    command = "INSERT INTO rentals (renter_id, rentee_id, vehicle_id, rental_start, rental_end) values (%s, %s, %s. %s. %s)"
    values = (renter_id, rentee_id, vehicle_id, rental_start, rental_end)
    cursor.execute(command, values)
    mydb.commit()
    return


# STATISTIC FUNCTIONS
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
    command = """SELECT c.car_plate, c.car_make, c.car_model, (datediff(r.rental_end, r.rental_start) / (YEAR(curdate())  -  c.car_year)) AS utilization_rate
        FROM cars c
        JOIN rentals r ON c.car_id = r.vehicle_id
        ORDER BY utilization_rate DESC
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


# ==============================================================================================


class CarRentalService(App):

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = CarRentalService()
    app.run()
