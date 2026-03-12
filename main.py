import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import socket

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_sales.db", check_same_thread=False)
cursor = conn.cursor()

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS creditors(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fuel_prices(
fuel TEXT UNIQUE,
price REAL
)
""")

conn.commit()

# ---------------- DEFAULT FUEL PRICES ----------------
default_prices = {"Petrol":100.0,"Diesel":90.0,"Power Petrol":105.0}

for fuel, price in default_prices.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_prices VALUES (?,?)",(fuel,price))

conn.commit()

# ---------------- SESSION STATE ----------------
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged=False

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump",layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp{
background-color:#ff6f00;
}
</style>
""",unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("⛽ Choisons Petrol Pump Management System")

st.info("""
Phone: +91 8590304889  
Email: kvpnaseeh@gmail.com / choisonscalicut@gmail.com  
Created by Nazeeh
""")

# ---------------- LOAD DATA ----------------
fuel_prices_df = pd.read_sql("SELECT * FROM fuel_prices",conn)
fuel_price_dict = dict(zip(fuel_prices_df['fuel'],fuel_prices_df['price']))

staff_list = pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
creditor_list = pd.read_sql("SELECT name FROM creditors",conn)["name"].tolist()

# ---------------- SALES ENTRY ----------------
st.subheader("Sales Entry")

col1,col2,col3 = st.columns(3)

with col1:
    staff = st.selectbox("Staff Name",staff_list if staff_list else ["No Staff"])

with col2:
    entry_date = st.date_input("Date",date.today())

with col3:
    fuel = st.selectbox("Fuel Type",["Petrol","Diesel","Power Petrol"])

price = fuel_price_dict.get(fuel,100)

nozzle = st.selectbox("Nozzle",[f"Nozzle {i}" for i in range(1,11)])

col4,col5 = st.columns(2)

with col4:
    opening = st.number_input("Opening Meter")

with col5:
    closing = st.number_input("Closing Meter")

litres = max(closing-opening,0)
total = litres*price

st.success(f"Litres Sold: {litres} L | Total ₹ {total}")

# ---------------- PAYMENT ----------------
st.subheader("Payment Details")

col1,col2,col3 = st.columns(3)

with col1:
    paytm = st.number_input("Paytm",0.0)

with col2:
    hp_pay = st.number_input("HP Pay",0.0)

with col3:
    cash = st.number_input("Cash",0.0)

credit = st.number_input("Credit",0.0)
advance_paid = st.number_input("Advance Paid",0.0)

balance_cash = total-(paytm+hp_pay+cash+advance_paid)

st.info(f"Balance Cash ₹ {balance_cash}")

creditor_name=""

if credit>0:
    if creditor_list:
        creditor_name = st.selectbox("Select Creditor",creditor_list)
    else:
        st.warning("No creditors added yet")

# ---------------- DUTY ----------------
duty_in = st.time_input("Duty IN")
duty_out = st.time_input("Duty OUT")

in_time = datetime.combine(date.today(),duty_in)
out_time = datetime.combine(date.today(),duty_out)

hours = max((out_time-in_time).total_seconds()/3600,0)

ip_address = socket.gethostbyname(socket.gethostname())

# ---------------- SAVE ----------------
if st.button("Save Entry"):

    cursor.execute("""
    INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,(str(entry_date),staff,fuel,nozzle,opening,closing,litres,price,total,
    paytm,hp_pay,cash,credit,advance_paid,balance_cash,creditor_name,
    str(duty_in),str(duty_out),hours,ip_address))

    conn.commit()

    st.success("Entry Saved")

# ---------------- LOAD SALES ----------------
df = pd.read_sql("SELECT rowid,* FROM sales",conn)

# ---------------- DASHBOARD ----------------
st.subheader("Dashboard Summary")

col1,col2,col3 = st.columns(3)

with col1:
    st.metric("Total Litres",df["litres"].sum())

with col2:
    st.metric("Total Sales ₹",df["total"].sum())

with col3:
    st.metric("Total Hours",df["hours"].sum())

# ---------------- PAYMENT SUMMARY ----------------
st.subheader("Payment Summary")

col1,col2,col3 = st.columns(3)

with col1:
    st.metric("Paytm",df["paytm"].sum())

with col2:
    st.metric("HP Pay",df["hp_pay"].sum())

with col3:
    st.metric("Cash",df["cash"].sum())

# ---------------- CREDIT REPORT ----------------
st.subheader("Creditors Outstanding")

credit_report = df.groupby("creditor_name")["credit"].sum().reset_index()

st.dataframe(credit_report)

# ---------------- DAILY REPORT ----------------
st.subheader("Search Daily Sales")

search_date = st.date_input("Select Date",date.today())

search_data = df[df["date"]==str(search_date)]

st.dataframe(search_data)

# ---------------- ADMIN SIDEBAR ----------------
st.sidebar.title("Admin Panel")

if not st.session_state.admin_logged:

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password",type="password")

    if st.sidebar.button("Login"):

        if username=="admin" and password=="admin123":
            st.session_state.admin_logged=True
            st.sidebar.success("Admin Logged In")
        else:
            st.sidebar.error("Invalid Login")

# ---------------- ADMIN CONTROLS ----------------
if st.session_state.admin_logged:

    st.sidebar.success("Admin Mode")

    if st.sidebar.button("Logout"):
        st.session_state.admin_logged=False

    st.sidebar.subheader("Add Staff")

    new_staff = st.sidebar.text_input("Staff Name")

    if st.sidebar.button("Add Staff"):
        try:
            cursor.execute("INSERT INTO staff(name) VALUES (?)",(new_staff,))
            conn.commit()
            st.sidebar.success("Staff Added")
        except:
            st.sidebar.error("Staff already exists")

    st.sidebar.subheader("Add Creditor")

    new_creditor = st.sidebar.text_input("Creditor Name")

    if st.sidebar.button("Add Creditor"):
        try:
            cursor.execute("INSERT INTO creditors(name) VALUES (?)",(new_creditor,))
            conn.commit()
            st.sidebar.success("Creditor Added")
        except:
            st.sidebar.error("Creditor exists")

    st.sidebar.subheader("Fuel Price Update")

    for fuel in ["Petrol","Diesel","Power Petrol"]:

        new_price = st.sidebar.number_input(f"{fuel} Price",value=fuel_price_dict.get(fuel,100.0))

        if st.sidebar.button(f"Update {fuel}"):

            cursor.execute("UPDATE fuel_prices SET price=? WHERE fuel=?",(new_price,fuel))

            conn.commit()

            st.sidebar.success(f"{fuel} price updated")

    st.subheader("Delete Sales Records")

    if not df.empty:

        del_id = st.selectbox("Select Record ID",df["rowid"])

        if st.button("Delete Record"):

            cursor.execute("DELETE FROM sales WHERE rowid=?",(del_id,))
            conn.commit()

            st.warning("Record Deleted")
