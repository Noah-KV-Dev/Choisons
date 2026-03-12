import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(page_title="HP Petrol Pump System", layout="wide")

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
creditor REAL,
balance REAL,
time_in TEXT,
time_out TEXT
)
""")

cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_price(fuel TEXT UNIQUE,price REAL)")

conn.commit()

# ---------------- DEFAULT FUELS ----------------

fuels = {
"Petrol":100,
"Diesel":90,
"Power Petrol":105,
"Oil":120
}

for f,p in fuels.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES(?,?)",(f,p))

conn.commit()

fuel_df = pd.read_sql("SELECT * FROM fuel_price", conn)
fuel_price = dict(zip(fuel_df["fuel"], fuel_df["price"]))

# ---------------- SESSION ----------------

if "admin" not in st.session_state:
    st.session_state.admin = False

if "checklist_done" not in st.session_state:
    st.session_state.checklist_done = False

if "checklist_date" not in st.session_state:
    st.session_state.checklist_date = str(date.today())

if st.session_state.checklist_date != str(date.today()):
    st.session_state.checklist_done = False
    st.session_state.checklist_date = str(date.today())

# ---------------- SIDEBAR MENU ----------------

menu = ["Sales Entry","Reports","Staff Daily Checklist"]

if st.session_state.admin:
    menu.append("Admin Controls")

page = st.sidebar.selectbox("Menu", menu)

# ---------------- ADMIN LOGIN ----------------

st.sidebar.markdown("---")
st.sidebar.subheader("Admin Access")

if not st.session_state.admin:

    password = st.sidebar.text_input("Admin Password", type="password")

    if st.sidebar.button("Login"):

        if password == "admin786":
            st.session_state.admin = True
            st.sidebar.success("Admin Logged In")
            st.rerun()
        else:
            st.sidebar.error("Wrong Password")

else:

    st.sidebar.success("Admin Logged In")

    if st.sidebar.button("Logout"):
        st.session_state.admin = False
        st.rerun()

# ---------------- SALES ENTRY ----------------

if page == "Sales Entry":

    st.title("Fuel Sales Entry")

    if not st.session_state.checklist_done:
        st.error("Sales Blocked — Complete Staff Daily Checklist")
        st.stop()

    staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()

    if len(staff_list) == 0:
        st.warning("No staff available. Admin must add staff.")
        st.stop()

    staff = st.selectbox("Staff", staff_list)

    col1,col2 = st.columns(2)

    with col1:
        time_in = st.time_input("Duty Time IN", datetime.now().time())

    with col2:
        time_out = st.time_input("Duty Time OUT", datetime.now().time())

    fuel = st.selectbox("Fuel Type", list(fuel_price.keys()))

    price = fuel_price[fuel]

    st.info(f"Fuel Price ₹ {price}")

    opening = st.number_input("Opening Meter",0.0)
    closing = st.number_input("Closing Meter",0.0)

    litres = max(closing-opening,0)
    total = litres*price

    st.success(f"Litres = {litres} | Amount = ₹ {total}")

    st.subheader("Payments")

    paytm = st.number_input("Paytm",0.0)
    sbi = st.number_input("SBI",0.0)
    hppay = st.number_input("HP Pay",0.0)
    advance = st.number_input("Advance Paid",0.0)
    creditor = st.number_input("Creditor",0.0)

    paid = paytm+sbi+hppay+advance+creditor
    balance = total-paid

    st.warning(f"Balance Cash ₹ {balance}")

    if st.button("Save Entry"):

        cursor.execute("""
        INSERT INTO sales VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
        str(date.today()),staff,fuel,opening,closing,litres,price,total,
        paytm,sbi,hppay,advance,creditor,balance,
        str(time_in),str(time_out)
        ))

        conn.commit()

        st.success("Entry Saved")

    # -------- QUICK REPORT --------

    st.markdown("---")
    st.subheader("Quick Daily Summary")

    df = pd.read_sql("SELECT * FROM sales", conn)

    today = df[df["date"] == str(date.today())]

    if len(today) > 0:

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("Total Sales", round(today["total"].sum(),2))
        c2.metric("Total Litres", round(today["litres"].sum(),2))
        c3.metric("Total Paytm", round(today["paytm"].sum(),2))
        c4.metric("Total Balance Cash", round(today["balance"].sum(),2))

# ---------------- REPORTS ----------------

elif page == "Reports":

    st.title("Reports")

    report_type = st.selectbox("Select Report",[
    "Daily Sales",
    "Staff Sales",
    "Fuel Sales",
    "Payment Summary"
    ])

    df = pd.read_sql("SELECT * FROM sales", conn)

    if len(df) == 0:
        st.warning("No data available")
        st.stop()

    if report_type == "Daily Sales":

        d = st.date_input("Date",date.today())

        r = df[df["date"] == str(d)].sort_values("staff")

        st.dataframe(r)

        st.write("Total ₹", r["total"].sum())

    elif report_type == "Staff Sales":

        r = df.groupby("staff")[["litres","total"]].sum()

        st.dataframe(r)

    elif report_type == "Fuel Sales":

        r = df.groupby("fuel")[["litres","total"]].sum()

        st.dataframe(r)

    elif report_type == "Payment Summary":

        payments = df[["paytm","sbi","hppay","advance","creditor","balance"]].sum()

        st.write(payments)

# ---------------- CHECKLIST ----------------

elif page == "Staff Daily Checklist":

    st.title("Staff Daily Checklist")

    checklist = [

    "Report on time in uniform",
    "Check pump machine condition",
    "Confirm fire extinguisher",
    "Show ZERO reading before fueling",
    "Customer engine OFF confirmed",
    "Fuel safely without spill",
    "Collect correct payment",
    "No mobile near pumps",
    "Report leakage immediately",
    "Keep pump area clean",
    "Submit machine reading to manager",
    "Hand over duty properly"

    ]

    checks = [st.checkbox(i) for i in checklist]

    if st.button("Apply Checklist"):

        if all(checks):
            st.session_state.checklist_done = True
            st.success("Checklist Completed — Sales Enabled")
        else:
            st.error("Checklist incomplete")

# ---------------- ADMIN CONTROLS ----------------

elif page == "Admin Controls":

    st.title("Admin Controls")

    st.subheader("Add Staff")

    new_staff = st.text_input("Staff Name")

    if st.button("Add Staff"):

        try:
            cursor.execute("INSERT INTO staff VALUES(?)",(new_staff,))
            conn.commit()
            st.success("Staff Added")
        except:
            st.error("Staff already exists")

    st.subheader("Remove Staff")

    staff_list = pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()

    if len(staff_list)>0:

        remove_staff = st.selectbox("Select Staff", staff_list)

        if st.button("Remove Staff"):

            cursor.execute("DELETE FROM staff WHERE name=?", (remove_staff,))
            conn.commit()

            st.success("Staff Removed")

    st.subheader("Fuel Price Change")

    for f in fuel_price:

        new_price = st.number_input(f,value=float(fuel_price[f]))

        if st.button(f"Update {f}"):

            cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?",(new_price,f))
            conn.commit()

            st.success(f"{f} price updated")
