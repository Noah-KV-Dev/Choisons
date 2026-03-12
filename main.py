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
advance_paid REAL,
balance_cash REAL,
duty_in TEXT,
duty_out TEXT,
hours REAL,
ip_address TEXT,
credit_sale REAL
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

cursor.execute("""
CREATE TABLE IF NOT EXISTS cash_closing(
date TEXT,
system_cash REAL,
closing_cash REAL,
shortage REAL,
ip_address TEXT
)
""")

conn.commit()

# ---------------- DEFAULT FUEL PRICES ----------------
default_prices = {"Petrol":100.0,"Diesel":90.0,"Power Petrol":105.0}
for fuel, price in default_prices.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_prices(fuel, price) VALUES (?, ?)", (fuel, price))
conn.commit()

# ---------------- PAGE ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

st.title("⛽ Choisons Petrol Pump Management System")

st.info("Phone: +91 8590304889  |  Email: kvpnaseeh@gmail.com / choisonscalicut@gmail.com  |  Created by Nazeeh")
# ---------------- FUNCTIONS ----------------
def load_data():
    df = pd.read_sql("SELECT rowid,* FROM sales", conn)

    if not df.empty:
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')

    return df


def export_excel(data):
    return data.to_csv(index=False).encode("utf-8")


# ---------------- LOAD DATA ----------------
df = load_data()

fuel_prices_df = pd.read_sql("SELECT * FROM fuel_prices", conn)
fuel_price_dict = dict(zip(fuel_prices_df['fuel'], fuel_prices_df['price']))

staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()

# ---------------- ADMIN SESSION ----------------
if "logged_in_admin" not in st.session_state:
    st.session_state.logged_in_admin = None

# ---------------- SIDEBAR ----------------
menu = ["Sales Entry","Reports & Summary"]

if st.session_state.logged_in_admin:
    menu.append("Admin Controls")

menu_option = st.sidebar.selectbox("Menu",menu)

# ---------------- ADMIN LOGIN ----------------
if not st.session_state.logged_in_admin:

    st.sidebar.subheader("Admin Login")

    admin_name = st.sidebar.text_input("Admin Username")
    admin_pass = st.sidebar.text_input("Password",type="password")

    if st.sidebar.button("Login"):

        if admin_pass == "admin786":

            login_time = datetime.now()
            ip = socket.gethostbyname(socket.gethostname())

            cursor.execute(
            "INSERT INTO admin_logs(admin_name,login_time,ip_address) VALUES (?,?,?)",
            (admin_name,str(login_time),ip)
            )

            conn.commit()

            st.session_state.logged_in_admin = admin_name

            st.sidebar.success("Admin Logged In")

            st.rerun()

        else:

            st.sidebar.error("Wrong Password")

else:

    if st.sidebar.button("Logout"):

        logout_time = datetime.now()

        cursor.execute("""
        UPDATE admin_logs 
        SET logout_time=? 
        WHERE admin_name=? AND logout_time IS NULL
        """,(str(logout_time),st.session_state.logged_in_admin))

        conn.commit()

        st.session_state.logged_in_admin = None

        st.rerun()

# ---------------- SALES ENTRY ----------------
if menu_option == "Sales Entry":

    st.subheader("Sales Entry")

    col1,col2,col3 = st.columns(3)

    with col1:
        staff = st.selectbox("Staff",staff_list)

    with col2:
        entry_date = st.date_input("Date",date.today())

    with col3:
        fuel = st.selectbox("Fuel",["Petrol","Diesel","Power Petrol"])

    price = fuel_price_dict.get(fuel,100)

    nozzle = st.selectbox("Nozzle",[f"Nozzle {i}" for i in range(1,11)])

    col4,col5 = st.columns(2)

    with col4:
        opening = st.number_input("Opening Meter",0.0)

    with col5:
        closing = st.number_input("Closing Meter",0.0)

    litres = max(closing-opening,0)

    total = litres*price

    st.success(f"Litres: {litres} | Total ₹ {total}")

    # -------- PAYMENTS --------
    st.subheader("Payments")

    col1,col2,col3,col4,col5 = st.columns(5)

    with col1:
        paytm = st.number_input("Paytm",0.0)

    with col2:
        hp_pay = st.number_input("HP Pay",0.0)

    with col3:
        cash = st.number_input("Cash",0.0)

    with col4:
        advance_paid = st.number_input("Advance",0.0)

    with col5:
        credit_sale = st.number_input("Credit Sale",0.0)

    balance_cash = max(total-(paytm+hp_pay+cash+advance_paid+credit_sale),0)

    st.info(f"Balance Cash ₹ {balance_cash}")

    duty_in = st.time_input("Duty IN")
    duty_out = st.time_input("Duty OUT")

    in_time = datetime.combine(date.today(),duty_in)
    out_time = datetime.combine(date.today(),duty_out)

    hours = max((out_time-in_time).total_seconds()/3600,0)

    ip = socket.gethostbyname(socket.gethostname())

    if st.button("Save Entry"):

        cursor.execute("""
        INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(str(entry_date),staff,fuel,nozzle,opening,closing,litres,price,total,
             paytm,hp_pay,cash,advance_paid,balance_cash,
             str(duty_in),str(duty_out),hours,ip,credit_sale))

        conn.commit()

        st.success("Saved")

        st.rerun()

    # -------- CASH SHORTAGE --------
    st.subheader("Daily Cash Closing")

    system_cash = paytm + hp_pay + cash

    closing_cash = st.number_input("Actual Cash in Hand",0.0)

    shortage = closing_cash-system_cash

    if st.button("Check Cash"):

        cursor.execute("""
        INSERT INTO cash_closing VALUES (?,?,?,?,?)
        """,(str(entry_date),system_cash,closing_cash,shortage,ip))

        conn.commit()

        if shortage == 0:

            st.success("Cash Perfect")

        elif shortage < 0:

            st.error(f"Cash Shortage ₹ {shortage}")

        else:

            st.warning(f"Extra Cash ₹ {shortage}")

# ---------------- REPORTS ----------------
elif menu_option == "Reports & Summary":

    st.subheader("Dashboard")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric("Total Litres",df["litres"].sum())

    with col2:
        st.metric("Total Sales ₹",df["total"].sum())

    with col3:
        st.metric("Total Hours",df["hours"].sum())

    st.subheader("Fuel Sales Chart")

    st.bar_chart(df.groupby("fuel")["litres"].sum())

    st.subheader("Staff Performance")

    st.bar_chart(df.groupby("staff")["total"].sum())

    st.subheader("Nozzle Sales")

    st.bar_chart(df.groupby("nozzle")["litres"].sum())

    st.subheader("Daily Data")

    st.dataframe(df)

    csv = export_excel(df)

    st.download_button(
    "Download Full Report",
    csv,
    "petrol_sales.csv",
    "text/csv"
    )

# ---------------- ADMIN CONTROLS ----------------
elif menu_option == "Admin Controls":

    st.subheader("Admin Controls")

    new_staff = st.text_input("Add Staff")

    if st.button("Add Staff"):

        try:

            cursor.execute("INSERT INTO staff(name) VALUES (?)",(new_staff,))

            conn.commit()

            st.success("Staff Added")

        except:

            st.error("Staff Exists")

    st.subheader("Update Fuel Prices")

    for fuel in ["Petrol","Diesel","Power Petrol"]:

        price = st.number_input(
        fuel,
        value=float(fuel_price_dict.get(fuel,100))
        )

        if st.button(f"Update {fuel}"):

            cursor.execute(
            "UPDATE fuel_prices SET price=? WHERE fuel=?",
            (price,fuel)
            )

            conn.commit()

            st.success(f"{fuel} price updated")
