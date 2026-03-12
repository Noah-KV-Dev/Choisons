import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import socket

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# -------- ENTER KEY AUTO SAVE --------
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === "Enter") {
        const btn = window.parent.document.querySelector('button[kind="primary"]');
        if(btn){btn.click();}
    }
});
</script>
""", unsafe_allow_html=True)

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
advance REAL,
balance_cash REAL,
duty_in TEXT,
duty_out TEXT,
hours REAL,
ip_address TEXT,
credit REAL
)
""")

cursor.execute("CREATE TABLE IF NOT EXISTS staff(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_prices(fuel TEXT UNIQUE,price REAL)")

conn.commit()

# ---------------- DEFAULT FUEL PRICES ----------------
default_prices = {"Petrol":100.0,"Diesel":90.0,"Power Petrol":105.0}

for fuel,price in default_prices.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_prices VALUES (?,?)",(fuel,price))

conn.commit()

# ---------------- CHECKLIST SESSION ----------------
if "checklist_done" not in st.session_state:
    st.session_state.checklist_done = False

if "missing_items" not in st.session_state:
    st.session_state.missing_items = []

# ---------------- FUNCTIONS ----------------
def load_data():
    df = pd.read_sql("SELECT rowid,* FROM sales", conn)
    if not df.empty:
        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
    return df

df = load_data()

fuel_prices_df = pd.read_sql("SELECT * FROM fuel_prices", conn)
fuel_price_dict = dict(zip(fuel_prices_df["fuel"],fuel_prices_df["price"]))

staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()

# ---------------- TITLE ----------------
st.title("⛽ Choisons Petrol Pump Management System")

# ---------------- ADMIN LOGIN ----------------
if "admin" not in st.session_state:
    st.session_state.admin = False

st.sidebar.subheader("Admin Login")

admin_pass = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if admin_pass == "admin786":
        st.session_state.admin = True
        st.sidebar.success("Admin Logged In")
    else:
        st.sidebar.error("Wrong Password")

if st.session_state.admin:
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin = False
        st.rerun()

# ---------------- MENU ----------------
menu = ["Sales Entry","Reports","HP Daily Staff Check List"]

if st.session_state.admin:
    menu.append("Admin Controls")

page = st.sidebar.selectbox("Menu", menu)

# ---------------- CHECKLIST PAGE ----------------
if page == "HP Daily Staff Check List":

    st.header("HP Daily Staff Check List")

    c1 = st.checkbox("Staff on time")
    c2 = st.checkbox("Proper uniform & ID card")
    c3 = st.checkbox("No mobile phone during duty")

    c4 = st.checkbox("Opening meter reading checked")
    c5 = st.checkbox("No leakage in nozzle")
    c6 = st.checkbox("Correct fuel delivery")

    c7 = st.checkbox("Opening cash verified")
    c8 = st.checkbox("Cash matches system sales")
    c9 = st.checkbox("UPI / Card machine working")

    c10 = st.checkbox("Fire extinguisher available")
    c11 = st.checkbox("No smoking in forecourt")
    c12 = st.checkbox("Emergency switch working")

    c13 = st.checkbox("Closing nozzle reading recorded")
    c14 = st.checkbox("Cash balance checked")
    c15 = st.checkbox("Daily report completed")

    if st.button("Apply Checklist"):

        missing = []

        checks = [
            (c1,"Staff not confirmed on time"),
            (c2,"Uniform not confirmed"),
            (c3,"Mobile rule not confirmed"),
            (c4,"Opening meter not checked"),
            (c5,"Nozzle leakage not confirmed"),
            (c6,"Fuel delivery not confirmed"),
            (c7,"Opening cash not verified"),
            (c8,"Cash matching not verified"),
            (c9,"UPI/Card machine not checked"),
            (c10,"Fire extinguisher not checked"),
            (c11,"No smoking rule not confirmed"),
            (c12,"Emergency switch not checked"),
            (c13,"Closing meter not confirmed"),
            (c14,"Cash balance not confirmed"),
            (c15,"Daily report not confirmed")
        ]

        for status,msg in checks:
            if not status:
                missing.append(msg)

        if len(missing)==0:
            st.session_state.checklist_done=True
            st.session_state.missing_items=[]
            st.success("Checklist Completed. Sales Entry Enabled.")
        else:
            st.session_state.checklist_done=False
            st.session_state.missing_items=missing
            st.error("Checklist incomplete")

# ---------------- SALES ENTRY ----------------
elif page == "Sales Entry":

    if not st.session_state.checklist_done:

        st.warning("Sales Entry Blocked")

        if st.session_state.missing_items:
            st.write("### Reason:")
            for m in st.session_state.missing_items:
                st.write("❌",m)

        st.stop()

    st.subheader("Fuel Entry")

    col1,col2,col3 = st.columns(3)

    with col1:
        staff = st.selectbox("Staff", staff_list)

    with col2:
        entry_date = st.date_input("Date", date.today())

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

    st.success(f"Litres: {litres} | Amount ₹ {total}")

    col1,col2,col3,col4,col5 = st.columns(5)

    with col1: paytm = st.number_input("Paytm",0.0)
    with col2: hp_pay = st.number_input("HP Pay",0.0)
    with col3: cash = st.number_input("Cash",0.0)
    with col4: advance = st.number_input("Advance",0.0)
    with col5: credit = st.number_input("Credit",0.0)

    balance_cash = max(total-(paytm+hp_pay+cash+advance+credit),0)

    st.info(f"Balance Cash ₹ {balance_cash}")

    duty_in = st.time_input("Duty IN")
    duty_out = st.time_input("Duty OUT")

    in_time = datetime.combine(date.today(), duty_in)
    out_time = datetime.combine(date.today(), duty_out)

    hours = max((out_time-in_time).total_seconds()/3600,0)

    ip = socket.gethostbyname(socket.gethostname())

    if st.button("Save Entry", type="primary"):

        cursor.execute("""
        INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(str(entry_date),staff,fuel,nozzle,opening,closing,litres,price,total,
             paytm,hp_pay,cash,advance,balance_cash,
             str(duty_in),str(duty_out),hours,ip,credit))

        conn.commit()

        st.success("Entry Saved")

        st.rerun()

# ---------------- REPORTS ----------------
elif page == "Reports":

    st.subheader("Dashboard")

    col1,col2,col3 = st.columns(3)

    with col1: st.metric("Total Litres", df["litres"].sum())
    with col2: st.metric("Total Sales ₹", df["total"].sum())
    with col3: st.metric("Total Hours", df["hours"].sum())

    st.subheader("Fuel Chart")
    st.bar_chart(df.groupby("fuel")["litres"].sum())

    st.subheader("Staff Performance")
    st.bar_chart(df.groupby("staff")["total"].sum())

# ---------------- ADMIN ----------------
elif page == "Admin Controls":

    st.subheader("Admin Controls")

    new_staff = st.text_input("Staff Name")

    if st.button("Add Staff"):
        try:
            cursor.execute("INSERT INTO staff(name) VALUES (?)",(new_staff,))
            conn.commit()
            st.success("Staff Added")
        except:
            st.error("Staff already exists")

    st.divider()

    staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()

    remove_staff = st.selectbox("Select Staff", staff_list)

    if st.button("Remove Staff"):
        cursor.execute("DELETE FROM staff WHERE name=?", (remove_staff,))
        conn.commit()
        st.success("Staff removed")
        st.rerun()
