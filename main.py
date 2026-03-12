import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import socket

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_sales.db", check_same_thread=False)
cursor = conn.cursor()

# Sales table (with vehicle_number)
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
ip_address TEXT,
vehicle_number TEXT
)
""")

# Staff table
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE
)
""")

# Creditors table
cursor.execute("""
CREATE TABLE IF NOT EXISTS creditors(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE
)
""")

# Fuel prices table
cursor.execute("""
CREATE TABLE IF NOT EXISTS fuel_prices(
fuel TEXT UNIQUE,
price REAL
)
""")

# Admin login/logout tracking
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
admin_name TEXT,
login_time TEXT,
logout_time TEXT,
ip_address TEXT
)
""")

conn.commit()

# ---------------- DEFAULT FUEL PRICES ----------------
default_prices = {"Petrol":100.0,"Diesel":90.0,"Power Petrol":105.0}
for fuel,price in default_prices.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_prices VALUES (?,?)",(fuel,price))
conn.commit()

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

# ---------------- TITLE ----------------
st.title("⛽ Choisons Petrol Pump Management System")
st.info("""
Phone: +91 8590304889  
Email: kvpnaseeh@gmail.com / choisonscalicut@gmail.com  
Created by Nazeeh
""")

# ---------------- LOAD DATA ----------------
fuel_prices_df = pd.read_sql("SELECT * FROM fuel_prices", conn)
fuel_price_dict = dict(zip(fuel_prices_df['fuel'], fuel_prices_df['price']))
staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()
creditor_list = pd.read_sql("SELECT name FROM creditors", conn)["name"].tolist()

# ---------------- SALES ENTRY ----------------
st.subheader("Sales Entry")
col1,col2,col3 = st.columns(3)
with col1: staff = st.selectbox("Staff Name", staff_list)
with col2: entry_date = st.date_input("Date", date.today())
with col3: fuel = st.selectbox("Fuel Type", ["Petrol","Diesel","Power Petrol"])
price = fuel_price_dict.get(fuel,100)
nozzle = st.selectbox("Nozzle",[f"Nozzle {i}" for i in range(1,11)])
col4,col5 = st.columns(2)
with col4: opening = st.number_input("Opening Meter")
with col5: closing = st.number_input("Closing Meter")
litres = max(closing-opening,0)
total = litres*price
st.success(f"Litres Sold: {litres} L | Total: ₹ {total}")

# ---------------- PAYMENT SECTION ----------------
st.subheader("Payment Details")
col1,col2,col3 = st.columns(3)
with col1: paytm = st.number_input("Paytm", 0.0)
with col2: hp_pay = st.number_input("HP Pay", 0.0)
with col3: cash = st.number_input("Cash", 0.0)
credit = st.number_input("Credit", 0.0)
advance_paid = st.number_input("Advance Paid", 0.0)
balance_cash = max(total - (paytm + hp_pay + cash + advance_paid + credit), 0)
st.info(f"Balance Cash: ₹ {balance_cash}")

creditor_name = ""
vehicle_number = ""
if credit > 0:
    if creditor_list:
        creditor_name = st.selectbox("Select Creditor", creditor_list)
        vehicle_number = st.text_input("Vehicle Number")
    else:
        st.warning("No creditors available. Contact admin to add a new creditor.")

# ---------------- DUTY ----------------
duty_in = st.time_input("Duty IN")
duty_out = st.time_input("Duty OUT")
in_time = datetime.combine(date.today(), duty_in)
out_time = datetime.combine(date.today(), duty_out)
hours = max((out_time-in_time).total_seconds()/3600,0)
ip_address = socket.gethostbyname(socket.gethostname())

# ---------------- SAVE ENTRY ----------------
if st.button("Save Entry"):
    cursor.execute("""
    INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        str(entry_date), staff, fuel, nozzle, opening, closing, litres, price, total,
        paytm, hp_pay, cash, credit, advance_paid, balance_cash, creditor_name,
        str(duty_in), str(duty_out), hours, ip_address, vehicle_number
    ))
    conn.commit()
    st.success("Entry Saved")

# ---------------- LOAD SALES ----------------
df = pd.read_sql("SELECT rowid,* FROM sales", conn)

# ---------------- ENSURE COLUMNS EXIST ----------------
for col in ["paytm","hp_pay","cash","credit","advance_paid","balance_cash","vehicle_number","creditor_name"]:
    if col not in df.columns:
        df[col] = 0 if col not in ["vehicle_number","creditor_name"] else ""
df["paytm"] = df["paytm"].fillna(0)
df["hp_pay"] = df["hp_pay"].fillna(0)
df["cash"] = df["cash"].fillna(0)
df["credit"] = df["credit"].fillna(0)
df["advance_paid"] = df["advance_paid"].fillna(0)
df["balance_cash"] = df["balance_cash"].fillna(0)
df["vehicle_number"] = df["vehicle_number"].fillna("")
df["creditor_name"] = df["creditor_name"].fillna("")

# ---------------- DASHBOARD ----------------
st.subheader("Dashboard Summary")
col1,col2,col3 = st.columns(3)
with col1: st.metric("Total Litres", df["litres"].sum())
with col2: st.metric("Total Sales ₹", df["total"].sum())
with col3: st.metric("Total Hours", df["hours"].sum())

# ---------------- PAYMENT SUMMARY ----------------
st.subheader("Payment Summary")
st.dataframe(df[["paytm","hp_pay","cash","credit","advance_paid","balance_cash"]].sum().to_frame().T)

# ---------------- STAFF SUMMARY ----------------
staff_summary = df.groupby("staff")[["litres","total","hours","paytm","hp_pay","cash","credit","advance_paid","balance_cash"]].sum().reset_index()
st.subheader("Staff Summary")
st.dataframe(staff_summary)

# ---------------- NOZZLE SUMMARY ----------------
st.subheader("Nozzle Sales")
nozzle_sales = df.groupby("nozzle")["litres"].sum().reset_index()
st.dataframe(nozzle_sales)

# ---------------- CREDITORS REPORT ----------------
credit_df = df[df["credit"]>0].copy()
if not credit_df.empty:
    credit_report = credit_df.groupby(["creditor_name","vehicle_number"])[["credit","balance_cash"]].sum().reset_index()
else:
    credit_report = pd.DataFrame(columns=["creditor_name","vehicle_number","credit","balance_cash"])
st.subheader("Creditors Outstanding")
st.dataframe(credit_report)

# ---------------- MONTHLY SUMMARY ----------------
st.subheader("Monthly Summary")
df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
monthly_summary = df.groupby('month')[["litres","total","paytm","hp_pay","cash","credit","advance_paid","balance_cash"]].sum().reset_index()
st.dataframe(monthly_summary)
latest_month = monthly_summary.iloc[-1]
st.metric("Litres Sold", latest_month["litres"])
st.metric("Total Sales ₹", latest_month["total"])
st.metric("Paytm", latest_month["paytm"])
st.metric("HP Pay", latest_month["hp_pay"])
st.metric("Cash", latest_month["cash"])
st.metric("Credit", latest_month["credit"])
st.metric("Advance Paid", latest_month["advance_paid"])
st.metric("Balance Cash", latest_month["balance_cash"])

# ---------------- DAILY SEARCH ----------------
st.subheader("Search Daily Sales")
search_date = st.date_input("Select Date", date.today())
search_data = df[df["date"]==str(search_date)]
st.dataframe(search_data)
st.metric("Litres Sold", search_data["litres"].sum())
st.metric("Total Sales", search_data["total"].sum())
st.metric("Paytm", search_data["paytm"].sum())
st.metric("HP Pay", search_data["hp_pay"].sum())
st.metric("Cash", search_data["cash"].sum())

# ---------------- STAFF SEARCH ----------------
st.subheader("Search Staff Sales")
selected_staff = st.selectbox("Select Staff", staff_list)
from_date = st.date_input("From Date", date.today())
to_date = st.date_input("To Date", date.today())
staff_data = df[(df["staff"]==selected_staff) & (df["date"]>=str(from_date)) & (df["date"]<=str(to_date))]
st.dataframe(staff_data)
st.metric("Litres", staff_data["litres"].sum())
st.metric("Sales", staff_data["total"].sum())

# ---------------- ADMIN PANEL ----------------
st.sidebar.title("Admin Panel")

# Track admin login status
if "logged_in_admin" not in st.session_state:
    st.session_state.logged_in_admin = None

# Admin Login
st.sidebar.subheader("Admin Login")
admin_name = st.sidebar.text_input("Admin Username")
if st.sidebar.button("Login as Admin"):
    login_time = datetime.now()
    ip_address = socket.gethostbyname(socket.gethostname())
    cursor.execute("INSERT INTO admin_logs(admin_name, login_time, ip_address) VALUES (?,?,?)", 
                   (admin_name, str(login_time), ip_address))
    conn.commit()
    st.session_state.logged_in_admin = admin_name
    st.sidebar.success(f"Admin {admin_name} logged in at {login_time.strftime('%H:%M:%S')}")

# Admin Logout
if st.session_state.logged_in_admin:
    if st.sidebar.button("Logout Admin"):
        logout_time = datetime.now()
        cursor.execute("UPDATE admin_logs SET logout_time=? WHERE admin_name=? AND logout_time IS NULL",
                       (str(logout_time), st.session_state.logged_in_admin))
        conn.commit()
        st.sidebar.success(f"Admin {st.session_state.logged_in_admin} logged out at {logout_time.strftime('%H:%M:%S')}")
        st.session_state.logged_in_admin = None

# ---------------- ADMIN CONTROLS (ONLY IF LOGGED IN) ----------------
if st.session_state.logged_in_admin:

    st.sidebar.subheader("Add Staff")
    new_staff = st.sidebar.text_input("Staff Name", key="new_staff")
    if st.sidebar.button("Add Staff"):
        try:
            cursor.execute("INSERT INTO staff(name) VALUES (?)",(new_staff,))
            conn.commit()
            st.sidebar.success("Staff Added")
        except:
            st.sidebar.error("Staff Exists")

    st.sidebar.subheader("Add Creditor")
    new_creditor = st.sidebar.text_input("Creditor Name", key="new_creditor")
    if st.sidebar.button("Add Creditor"):
        try:
            cursor.execute("INSERT INTO creditors(name) VALUES (?)",(new_creditor,))
            conn.commit()
            st.sidebar.success("Creditor Added")
        except:
            st.sidebar.error("Creditor Exists")

    st.sidebar.subheader("Update Fuel Prices")
    for fuel in ["Petrol","Diesel","Power Petrol"]:
        new_price = st.sidebar.number_input(f"{fuel} Price", value=fuel_price_dict.get(fuel,100.0), key=f"price_{fuel}")
        if st.sidebar.button(f"Update {fuel}"):
            cursor.execute("UPDATE fuel_prices SET price=? WHERE fuel=?",(new_price,fuel))
            conn.commit()
            st.sidebar.success(f"{fuel} price updated")
else:
    st.sidebar.info("Login as admin to manage staff, creditors, and fuel prices")
