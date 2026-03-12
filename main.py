import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import socket

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_sales.db", check_same_thread=False)
cursor = conn.cursor()

# Sales Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
date TEXT,
staff TEXT,
fuel TEXT,
nozzle TEXT,
opening REAL,
closing REAL,
litres REAL,
price REAL,
total REAL,
paytm REAL,
hp_pay REAL,
cash REAL,
credit REAL,
advance_paid REAL,
balance_cash REAL,
creditor_name TEXT,
duty_in TEXT,
duty_out TEXT,
hours REAL,
ip_address TEXT
)
""")

# Staff Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE
)
""")

# Creditors Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS creditors(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE
)
""")

# Fuel Prices Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS fuel_prices(
fuel TEXT UNIQUE,
price REAL
)
""")

conn.commit()

# ---------------- DEFAULT FUEL PRICES ----------------
default_prices = {"Petrol":100.0, "Diesel":90.0, "Power Petrol":105.0}
for fuel, price in default_prices.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_prices(fuel, price) VALUES (?,?)", (fuel, price))
conn.commit()

# ---------------- SESSION STATE ----------------
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "rerun_flag" not in st.session_state:
    st.session_state.rerun_flag = False

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
html,body,[class*="css"]{
font-family:sans-serif;
color:black;
}
.stApp{
background-color:#ff6f00;
}
</style>
""", unsafe_allow_html=True)

# ---------------- ADMIN SIDEBAR ----------------
st.sidebar.title("Admin Panel")

# Load data for dynamic lists
staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()
creditor_list = pd.read_sql("SELECT name FROM creditors", conn)["name"].tolist()
fuel_prices_df = pd.read_sql("SELECT * FROM fuel_prices", conn)
fuel_price_dict = dict(zip(fuel_prices_df['fuel'], fuel_prices_df['price']))

if not st.session_state.admin_logged:
    st.sidebar.subheader("Admin Login")
    username = st.sidebar.text_input("Username", key="login_user")
    password = st.sidebar.text_input("Password", type="password", key="login_pass")
    if st.sidebar.button("Login", key="login_btn"):
        if username == "admin" and password == "admin123":
            st.session_state.admin_logged = True
            st.sidebar.success("Admin Logged In")
            st.experimental_rerun()
   else:
    st.sidebar.success("Admin Mode")
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.admin_logged = False
        st.experimental_rerun()

    # Admin Options
    st.sidebar.subheader("Add Staff")
    new_staff = st.sidebar.text_input("Staff Name", key="staff_add")
    if st.sidebar.button("Add Staff", key="add_staff_btn"):
        if new_staff.strip():
            try:
                cursor.execute("INSERT INTO staff(name) VALUES (?)", (new_staff.strip(),))
                conn.commit()
                st.sidebar.success(f"Staff '{new_staff}' added")
                st.experimental_rerun()
            except sqlite3.IntegrityError:
                st.sidebar.error("Staff already exists")

    st.sidebar.subheader("Add Creditor")
    new_creditor = st.sidebar.text_input("Creditor Name", key="creditor_add")
    if st.sidebar.button("Add Creditor", key="add_creditor_btn"):
        if new_creditor.strip():
            try:
                cursor.execute("INSERT INTO creditors(name) VALUES (?)", (new_creditor.strip(),))
                conn.commit()
                st.sidebar.success(f"Creditor '{new_creditor}' added")
                st.experimental_rerun()
            except sqlite3.IntegrityError:
                st.sidebar.error("Creditor already exists")

    st.sidebar.subheader("Fuel Price Update")
    for fuel in ["Petrol", "Diesel", "Power Petrol"]:
        new_price = st.sidebar.number_input(f"{fuel} Price", value=fuel_price_dict.get(fuel, 100.0), key=f"{fuel}_price")
        if st.sidebar.button(f"Update {fuel} Price", key=f"update_{fuel}"):
            cursor.execute("UPDATE fuel_prices SET price=? WHERE fuel=?", (new_price, fuel))
            conn.commit()
            st.sidebar.success(f"{fuel} price updated")
            st.experimental_rerun()

    # Delete Sales Records
    st.sidebar.subheader("Delete Sales Record")
    df = pd.read_sql("SELECT rowid,* FROM sales", conn)
    if not df.empty:
        del_id = st.sidebar.selectbox("Select Record ID", df["rowid"], key="delete_id")
        if st.sidebar.button("Delete Record", key="delete_btn"):
            cursor.execute("DELETE FROM sales WHERE rowid=?", (del_id,))
            conn.commit()
            st.sidebar.warning("Record Deleted")
            st.experimental_rerun()

# ---------------- MAIN SALES ENTRY ----------------
st.title("⛽ Choisons Petrol Pump Management System")
st.info("""
Phone: +91 8590304889  
Email: kvpnaseeh@gmail.com / choisonscalicut@gmail.com  
Created by Nazeeh
""")

st.subheader("Sales Entry")
col1, col2, col3 = st.columns(3)
with col1:
    staff = st.selectbox("Staff Name", staff_list if staff_list else ["No Staff"])
with col2:
    entry_date = st.date_input("Date", date.today())
with col3:
    fuel = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Power Petrol"])

price = fuel_price_dict.get(fuel, 100)
nozzle = st.selectbox("Nozzle", [f"Nozzle {i}" for i in range(1, 11)])

col4, col5 = st.columns(2)
with col4:
    opening = st.number_input("Opening Meter")
with col5:
    closing = st.number_input("Closing Meter")

litres = max(closing - opening, 0)
total = litres * price
st.success(f"Litres Sold: {litres} L | Total: ₹ {total}")

# Payment Section
st.subheader("Payment Details")
col1, col2, col3 = st.columns(3)
with col1:
    paytm = st.number_input("Paytm", 0.0)
with col2:
    hp_pay = st.number_input("HP Pay", 0.0)
with col3:
    cash = st.number_input("Cash", 0.0)

credit = st.number_input("Credit", 0.0)
advance_paid = st.number_input("Advance Paid", 0.0)
balance_cash = total - (paytm + hp_pay + cash + advance_paid)
st.info(f"Balance Cash: ₹ {balance_cash}")

creditor_name = ""
if credit > 0 and creditor_list:
    creditor_name = st.selectbox("Creditor Name", creditor_list)
elif credit > 0:
    st.warning("No creditors available. Ask admin to add.")

# Duty Hours
duty_in = st.time_input("Duty IN")
duty_out = st.time_input("Duty OUT")
in_time = datetime.combine(date.today(), duty_in)
out_time = datetime.combine(date.today(), duty_out)
hours = max((out_time - in_time).total_seconds() / 3600, 0)
ip_address = socket.gethostbyname(socket.gethostname())

# Save Entry
if st.button("Save Entry"):
    cursor.execute("""
    INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (str(entry_date), staff, fuel, nozzle, opening, closing, litres, price, total,
          paytm, hp_pay, cash, credit, advance_paid, balance_cash, creditor_name,
          str(duty_in), str(duty_out), hours, ip_address))
    conn.commit()
    st.success("Entry Saved")
    st.session_state.rerun_flag = True

# Load Sales for reports
df = pd.read_sql("SELECT rowid,* FROM sales", conn)

# ---------------- DASHBOARD ----------------
st.subheader("Dashboard Summary")
col1, col2, col3 = st.columns(3)
with col1: st.metric("Total Litres", df["litres"].sum())
with col2: st.metric("Total Sales ₹", df["total"].sum())
with col3: st.metric("Total Hours", df["hours"].sum())

st.subheader("Payment Summary")
col1, col2, col3 = st.columns(3)
with col1: st.metric("Paytm", df["paytm"].sum())
with col2: st.metric("HP Pay", df["hp_pay"].sum())
with col3: st.metric("Cash", df["cash"].sum())
col4, col5 = st.columns(2)
with col4: st.metric("Credit", df["credit"].sum())
with col5: st.metric("Advance Paid", df["advance_paid"].sum())

st.subheader("Staff Summary")
if not df.empty:
    staff_summary = df.groupby("staff")[["litres", "total", "hours"]].sum().reset_index()
    st.dataframe(staff_summary)

st.subheader("Nozzle Sales")
if not df.empty:
    nozzle_sales = df.groupby("nozzle")["litres"].sum().reset_index()
    st.dataframe(nozzle_sales)

st.subheader("Creditors Outstanding")
if not df.empty:
    credit_report = df.groupby("creditor_name")["credit"].sum().reset_index()
    st.dataframe(credit_report)

# ---------------- DAILY SEARCH ----------------
st.subheader("Search Daily Sales")
search_date = st.date_input("Select Date", date.today(), key="daily")
search_data = df[df["date"] == str(search_date)]
st.dataframe(search_data)
st.metric("Litres Sold", search_data["litres"].sum())
st.metric("Total Sales", search_data["total"].sum())
st.metric("Paytm", search_data["paytm"].sum())
st.metric("HP Pay", search_data["hp_pay"].sum())
st.metric("Cash", search_data["cash"].sum())

# ---------------- STAFF SEARCH ----------------
st.subheader("Search Staff Sales")
selected_staff = st.selectbox("Select Staff", staff_list if staff_list else ["None"])
col1, col2 = st.columns(2)
with col1: from_date = st.date_input("From Date", date.today(), key="from_date")
with col2: to_date = st.date_input("To Date", date.today(), key="to_date")
staff_data = df[(df["staff"] == selected_staff) &
                (df["date"] >= str(from_date)) &
                (df["date"] <= str(to_date))]
st.dataframe(staff_data)
st.metric("Litres", staff_data["litres"].sum())
st.metric("Sales", staff_data["total"].sum())

# ---------------- SAFE RERUN ----------------
if st.session_state.rerun_flag:
    st.session_state.rerun_flag = False
    st.experimental_rerun()
