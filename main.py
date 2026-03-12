import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

st.set_page_config(page_title="Petrol Pump System", layout="wide")

# ---------------- DATABASE ----------------

conn = sqlite3.connect("petrol_system.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
date TEXT,
staff TEXT,
fuel TEXT,
opening REAL,
closing REAL,
litres REAL,
price REAL,
total REAL,
paytm REAL,
sbi REAL,
hppay REAL,
advance REAL,
balance REAL
)
""")

cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_price(fuel TEXT UNIQUE,price REAL)")

conn.commit()

# ---------------- DEFAULT DATA ----------------

cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES('Petrol',100)")
cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES('Diesel',90)")
conn.commit()

fuel_df = pd.read_sql("SELECT * FROM fuel_price", conn)
fuel_price = dict(zip(fuel_df["fuel"], fuel_df["price"]))

# ---------------- SESSION STATES ----------------

if "admin" not in st.session_state:
    st.session_state.admin = False

if "checklist_applied" not in st.session_state:
    st.session_state.checklist_applied = False

if "checklist_date" not in st.session_state:
    st.session_state.checklist_date = str(date.today())

# reset checklist daily
if st.session_state.checklist_date != str(date.today()):
    st.session_state.checklist_applied = False
    st.session_state.checklist_date = str(date.today())

# ---------------- CHECKLIST ITEMS ----------------

checklist_items = [

"Report on time in clean uniform with ID badge",
"Guide vehicles to maintain smooth queue",
"Check assigned pump machine condition",
"Verify area is clean and hazard-free",
"Confirm fire extinguisher location",
"Greet customer politely and confirm fuel type",
"Show ZERO reading before fueling",
"Ask customer to switch off engine",
"Insert nozzle properly and fuel safely",
"Stop exactly at requested amount",
"Avoid fuel spoillage or overfilling",
"Return nozzle and close cap if needed",
"Collect correct payment",
"Count cash in front of customer",
"Issue receipt when required",
"Inform cashier/manager for any issue",
"Thank customer before they leave",
"No smoking or mobile use near pumps",
"Report leakage or machine fault immediately",
"Do not argue with customers call manager",
"Follow all safety procedures of Hindustan Petroleum",
"Keep pump area clean",
"Report machine reading to manager",
"Submit pending receipts or issues",
"Hand over duty properly to next staff"

]

# ---------------- SIDEBAR MENU ----------------

menu = ["Sales Entry", "Reports", "Staff Daily Checklist"]

if st.session_state.admin:
    menu.append("Admin Controls")

page = st.sidebar.selectbox("Menu", menu)

# ---------------- SALES ENTRY ----------------

if page == "Sales Entry":

    st.title("Fuel Sales Entry")

    if not st.session_state.checklist_applied:
        st.error("Sales Blocked: Complete Staff Daily Checklist First")
        st.stop()

    staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()

    if len(staff_list) == 0:
        st.warning("No staff added. Admin must add staff first.")
        st.stop()

    staff = st.selectbox("Staff", staff_list)

    fuel = st.selectbox("Fuel Type", list(fuel_price.keys()))

    price = fuel_price[fuel]

    st.info(f"Fuel Price ₹ {price}")

    opening = st.number_input("Opening Meter", 0.0)

    closing = st.number_input("Closing Meter", 0.0)

    litres = max(closing - opening, 0)

    total = litres * price

    st.success(f"Litres = {litres} | Amount = ₹ {total}")

    st.subheader("Payments")

    paytm = st.number_input("Paytm", 0.0)
    sbi = st.number_input("SBI", 0.0)
    hppay = st.number_input("HP Pay", 0.0)
    advance = st.number_input("Advance Paid", 0.0)

    paid = paytm + sbi + hppay + advance

    balance = total - paid

    st.warning(f"Balance Cash ₹ {balance}")

    if st.button("Save Entry"):

        cursor.execute("""
        INSERT INTO sales VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
        str(date.today()), staff, fuel, opening, closing, litres,
        price, total, paytm, sbi, hppay, advance, balance
        ))

        conn.commit()

        st.success("Sales Entry Saved")

# ---------------- REPORTS ----------------

elif page == "Reports":

    st.title("Daily Sales Report")

    df = pd.read_sql("SELECT * FROM sales", conn)

    if len(df) > 0:

        selected_date = st.date_input("Select Date", date.today())

        report = df[df["date"] == str(selected_date)]

        if len(report) > 0:

            report = report.sort_values("staff")

            st.dataframe(report)

            st.write("Total Sales ₹", report["total"].sum())

# ---------------- CHECKLIST ----------------

elif page == "Staff Daily Checklist":

    st.title("Staff Daily Checklist")

    checks = []

    for item in checklist_items:
        checks.append(st.checkbox(item))

    if st.button("Apply Checklist"):

        if all(checks):
            st.session_state.checklist_applied = True
            st.success("Checklist Completed. Sales Enabled.")
        else:
            st.error("Checklist incomplete. Sales still blocked.")

# ---------------- ADMIN CONTROLS ----------------

elif page == "Admin Controls":

    st.title("Admin Controls")

    st.subheader("Add Staff")

    new_staff = st.text_input("Staff Name")

    if st.button("Add Staff"):

        try:
            cursor.execute("INSERT INTO staff VALUES(?)", (new_staff,))
            conn.commit()
            st.success("Staff Added")
        except:
            st.error("Staff already exists")

    st.subheader("Remove Staff")

    staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()

    if len(staff_list) > 0:

        remove_staff = st.selectbox("Select Staff", staff_list)

        if st.button("Remove Staff"):
            cursor.execute("DELETE FROM staff WHERE name=?", (remove_staff,))
            conn.commit()
            st.success("Staff Removed")

    st.subheader("Fuel Price Control")

    for fuel in fuel_price:

        new_price = st.number_input(fuel, value=float(fuel_price[fuel]))

        if st.button(f"Update {fuel}"):

            cursor.execute(
                "UPDATE fuel_price SET price=? WHERE fuel=?",
                (new_price, fuel)
            )

            conn.commit()

            st.success(f"{fuel} price updated")

# ---------------- ADMIN LOGIN (BOTTOM SIDEBAR) ----------------

st.sidebar.markdown("---")
st.sidebar.subheader("Admin Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):

    if password == "admin786":
        st.session_state.admin = True
        st.sidebar.success("Admin Logged In")
    else:
        st.sidebar.error("Wrong Password")

if st.session_state.admin:

    if st.sidebar.button("Logout"):
        st.session_state.admin = False
        st.rerun()
