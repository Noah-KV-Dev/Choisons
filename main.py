import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import socket

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_sales.db", check_same_thread=False)
cursor = conn.cursor()

# Tables
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
cursor.execute("CREATE TABLE IF NOT EXISTS staff(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS creditors(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_prices(fuel TEXT UNIQUE,price REAL)")
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

# Default fuel prices
default_prices = {"Petrol":100.0,"Diesel":90.0,"Power Petrol":105.0}
for fuel,price in default_prices.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_prices VALUES (?,?)",(fuel,price))
conn.commit()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")
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
st.title("⛽ Choisons Petrol Pump Management System")
st.info("Phone: +91 8590304889  |  Email: kvpnaseeh@gmail.com / choisonscalicut@gmail.com  |  Created by Nazeeh")

# ---------------- LOAD DATA ----------------
def load_data():
    df = pd.read_sql("SELECT rowid,* FROM sales", conn)
    for col in ["paytm","hp_pay","cash","credit","advance_paid","balance_cash","vehicle_number","creditor_name"]:
        if col not in df.columns:
            df[col] = 0 if col not in ["vehicle_number","creditor_name"] else ""
    df.fillna({"paytm":0,"hp_pay":0,"cash":0,"credit":0,"advance_paid":0,"balance_cash":0,"vehicle_number":"","creditor_name":""}, inplace=True)
    return df

fuel_prices_df = pd.read_sql("SELECT * FROM fuel_prices", conn)
fuel_price_dict = dict(zip(fuel_prices_df['fuel'], fuel_prices_df['price']))
staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()
creditor_list = pd.read_sql("SELECT name FROM creditors", conn)["name"].tolist()
df = load_data()

# ---------------- SIDEBAR MENU ----------------
menu_option = st.sidebar.selectbox("Menu", ["Sales Entry", "Reports & Summary"])

# ---------------- ADMIN LOGIN (Sidebar) ----------------
if "logged_in_admin" not in st.session_state:
    st.session_state.logged_in_admin = None

st.sidebar.subheader("Admin Login")
admin_name = st.sidebar.text_input("Admin Username")
admin_password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login as Admin"):
    if admin_password == "admin786":
        login_time = datetime.now()
        ip_address = socket.gethostbyname(socket.gethostname())
        cursor.execute("INSERT INTO admin_logs(admin_name, login_time, ip_address) VALUES (?,?,?)", 
                       (admin_name, str(login_time), ip_address))
        conn.commit()
        st.session_state.logged_in_admin = admin_name
        st.sidebar.success(f"Admin {admin_name} logged in at {login_time.strftime('%H:%M:%S')}")
    else:
        st.sidebar.error("Incorrect Password!")

if st.session_state.logged_in_admin:
    if st.sidebar.button("Logout Admin"):
        logout_time = datetime.now()
        cursor.execute("UPDATE admin_logs SET logout_time=? WHERE admin_name=? AND logout_time IS NULL",
                       (str(logout_time), st.session_state.logged_in_admin))
        conn.commit()
        st.sidebar.success(f"Admin {st.session_state.logged_in_admin} logged out at {logout_time.strftime('%H:%M:%S')}")
        st.session_state.logged_in_admin = None

# ---------------- SALES ENTRY ----------------
if menu_option == "Sales Entry":
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

    # Payment
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
    if credit>0:
        if creditor_list:
            creditor_name = st.selectbox("Select Creditor", creditor_list)
        else:
            st.warning("No creditors available. Admin must add creditors.")
        vehicle_number = st.text_input("Vehicle Number")

    duty_in = st.time_input("Duty IN")
    duty_out = st.time_input("Duty OUT")
    in_time = datetime.combine(date.today(), duty_in)
    out_time = datetime.combine(date.today(), duty_out)
    hours = max((out_time-in_time).total_seconds()/3600,0)
    ip_address = socket.gethostbyname(socket.gethostname())

    if st.button("Save Entry"):
        cursor.execute("""INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
            str(entry_date), staff, fuel, nozzle, opening, closing, litres, price, total,
            paytm, hp_pay, cash, credit, advance_paid, balance_cash, creditor_name,
            str(duty_in), str(duty_out), hours, ip_address, vehicle_number
        ))
        conn.commit()
        st.success("Entry Saved")
        df = load_data()
        st.experimental_rerun()

    # ---------------- DAILY SUMMARY ----------------
    st.subheader("Daily Summary (Per Staff)")
    daily_data = df[df["date"]==str(date.today())]
    if not daily_data.empty:
        daily_summary = daily_data.groupby(["date","staff"])[["litres","total","paytm","hp_pay","cash","credit","advance_paid","balance_cash","hours"]].sum().reset_index()
        st.dataframe(daily_summary)
    else:
        st.info("No sales today.")

    # ---------------- MONTHLY SUMMARY ----------------
    st.subheader("Monthly Summary (Per Staff)")
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    month_period = pd.Period(str(date.today()), freq='M')
    monthly_data = df[df['month']==month_period]
    if not monthly_data.empty:
        monthly_summary = monthly_data.groupby(["month","staff"])[["litres","total","paytm","hp_pay","cash","credit","advance_paid","balance_cash","hours"]].sum().reset_index()
        st.dataframe(monthly_summary)
    else:
        st.info("No sales this month.")

# ---------------- REPORTS & SUMMARY ----------------
elif menu_option == "Reports & Summary":
    st.subheader("Dashboard Summary")
    col1,col2,col3 = st.columns(3)
    with col1: st.metric("Total Litres", df["litres"].sum())
    with col2: st.metric("Total Sales ₹", df["total"].sum())
    with col3: st.metric("Total Hours", df["hours"].sum())

    st.subheader("Payment Summary")
    st.dataframe(df[["paytm","hp_pay","cash","credit","advance_paid","balance_cash"]].sum().to_frame().T)

    st.subheader("Staff Summary")
    staff_summary = df.groupby(["date","staff"])[["litres","total","hours","paytm","hp_pay","cash","credit","advance_paid","balance_cash"]].sum().reset_index()
    st.dataframe(staff_summary)

    st.subheader("Nozzle Sales")
    nozzle_sales = df.groupby(["date","nozzle"])["litres"].sum().reset_index()
    st.dataframe(nozzle_sales)

    st.subheader("Creditors Outstanding (with Vehicle Details)")
    credit_df = df[df["credit"]>0].copy()
    if not credit_df.empty:
        credit_report = credit_df[["date","staff","creditor_name","vehicle_number","credit","balance_cash"]]
        st.dataframe(credit_report)
        st.subheader("Vehicle-wise Credit Summary")
        vehicle_summary = credit_df.groupby("vehicle_number")[["credit","balance_cash"]].sum().reset_index()
        st.dataframe(vehicle_summary)
    else:
        st.info("No credit records found.")

    st.subheader("Monthly Summary")
    monthly_summary = df.groupby(["month","staff"])[["litres","total","paytm","hp_pay","cash","credit","advance_paid","balance_cash","hours"]].sum().reset_index()
    st.dataframe(monthly_summary)

# ---------------- ADMIN CONTROLS ----------------
if st.session_state.logged_in_admin:
    st.subheader(f"Admin Controls ({st.session_state.logged_in_admin})")
    st.text("Only logged-in admin can manage staff, creditors, and fuel prices")

    # Add Staff
    st.subheader("Add Staff")
    new_staff = st.text_input("Staff Name", key="new_staff")
    if st.button("Add Staff"):
        try:
            cursor.execute("INSERT INTO staff(name) VALUES (?)",(new_staff,))
            conn.commit()
            st.success("Staff Added")
        except:
            st.error("Staff Exists")

    # Add Creditor
    st.subheader("Add Creditor")
    new_creditor = st.text_input("Creditor Name", key="new_creditor")
    if st.button("Add Creditor"):
        try:
            cursor.execute("INSERT INTO creditors(name) VALUES (?)",(new_creditor,))
            conn.commit()
            st.success("Creditor Added")
        except:
            st.error("Creditor Exists")

    # Update Fuel Prices
    st.subheader("Update Fuel Prices")
    for fuel in ["Petrol","Diesel","Power Petrol"]:
        new_price = st.number_input(f"{fuel} Price", value=fuel_price_dict.get(fuel,100.0), key=f"price_{fuel}")
        if st.button(f"Update {fuel}"):
            cursor.execute("UPDATE fuel_prices SET price=? WHERE fuel=?",(new_price,fuel))
            conn.commit()
            st.success(f"{fuel} price updated")
