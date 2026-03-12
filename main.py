import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

st.set_page_config(page_title="Petrol Pump System",layout="wide")

# ---------------- DATABASE ----------------

conn = sqlite3.connect("petrol_system.db",check_same_thread=False)
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
cash REAL,
upi REAL,
card REAL
)
""")

cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_price(fuel TEXT UNIQUE,price REAL)")

conn.commit()

# -------- DEFAULT FUEL PRICES --------

cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES('Petrol',100)")
cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES('Diesel',90)")
conn.commit()

fuel_df=pd.read_sql("SELECT * FROM fuel_price",conn)
fuel_price=dict(zip(fuel_df["fuel"],fuel_df["price"]))

# ---------------- CHECKLIST ----------------

CHECKLIST_ITEMS=[

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
"Collect correct payment (cash/UPI/card)",
"Count cash in front of customer",
"Issue receipt when required",
"Inform cashier/manager for any issue",
"Thank customer before they leave",
"No smoking or mobile use near pumps",
"Report leakage or machine fault immediately",
"Do not argue with customers call manager",
"Follow all safety procedures of HP",
"Keep pump area clean",
"Report machine reading to manager",
"Submit pending receipts or issues",
"Hand over duty properly to next staff"

]

if "checklist_date" not in st.session_state:
    st.session_state.checklist_date=str(date.today())
    st.session_state.checklist_state={i:False for i in CHECKLIST_ITEMS}
    st.session_state.checklist_applied=False

if st.session_state.checklist_date!=str(date.today()):
    st.session_state.checklist_date=str(date.today())
    st.session_state.checklist_state={i:False for i in CHECKLIST_ITEMS}
    st.session_state.checklist_applied=False

# ---------------- ADMIN LOGIN ----------------

if "admin" not in st.session_state:
    st.session_state.admin=False

st.sidebar.title("Admin Login")

user=st.sidebar.text_input("Username")
pwd=st.sidebar.text_input("Password",type="password")

if st.sidebar.button("Login"):
    if pwd=="admin786":
        st.session_state.admin=True
        st.sidebar.success("Admin Logged In")

if st.session_state.admin:
    if st.sidebar.button("Logout"):
        st.session_state.admin=False
        st.rerun()

# ---------------- MENU ----------------

menu=["Sales Entry","Reports","Staff Daily Checklist"]

if st.session_state.admin:
    menu.append("Admin Controls")

page=st.sidebar.selectbox("Menu",menu)

# ---------------- SALES ENTRY ----------------

if page=="Sales Entry":

    st.title("Fuel Sales Entry")

    if not st.session_state.checklist_applied:

        missing=[k for k,v in st.session_state.checklist_state.items() if not v]

        if missing:
            st.error("Sales Blocked. Complete Staff Daily Checklist First")
            for m in missing:
                st.write("-",m)
            st.stop()

    staff_list=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()

    staff=st.selectbox("Staff",staff_list)

    fuel=st.selectbox("Fuel Type",list(fuel_price.keys()))

    price=fuel_price[fuel]

    st.info(f"Fuel Price ₹ {price}")

    opening=st.number_input("Opening Meter",0.0)

    closing=st.number_input("Closing Meter",0.0)

    litres=max(closing-opening,0)

    total=litres*price

    st.success(f"Litres {litres} | Amount ₹ {total}")

    cash=st.number_input("Cash",0.0)

    upi=st.number_input("UPI",0.0)

    card=st.number_input("Card",0.0)

    if st.button("Save Entry"):

        cursor.execute("""
        INSERT INTO sales VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """,(str(date.today()),staff,fuel,opening,closing,litres,price,total,cash,upi,card))

        conn.commit()

        st.success("Entry Saved")

# ---------------- REPORTS ----------------

elif page=="Reports":

    st.title("Sales Reports")

    df=pd.read_sql("SELECT * FROM sales",conn)

    if not df.empty:

        day=st.date_input("Select Date",date.today())

        daily=df[df["date"]==str(day)]

        if not daily.empty:

            daily=daily.sort_values("staff")

            st.dataframe(daily)

            st.write("Total Sales ₹",daily["total"].sum())

        st.subheader("Fuel Sales")

        st.bar_chart(df.groupby("fuel")["litres"].sum())

        st.subheader("Staff Sales")

        st.bar_chart(df.groupby("staff")["total"].sum())

# ---------------- CHECKLIST ----------------

elif page=="Staff Daily Checklist":

    st.title("Staff Daily Checklist")

    state=st.session_state.checklist_state

    for item in CHECKLIST_ITEMS:
        state[item]=st.checkbox(item,value=state[item])

    if st.button("Apply Checklist"):

        missing=[k for k,v in state.items() if not v]

        if missing:
            st.error("Checklist incomplete")
            for m in missing:
                st.write("-",m)
        else:
            st.session_state.checklist_applied=True
            st.success("Checklist Applied. Sales Entry Enabled")

# ---------------- ADMIN CONTROLS ----------------

elif page=="Admin Controls":

    st.title("Admin Controls")

    st.subheader("Add Staff")

    new_staff=st.text_input("Staff Name")

    if st.button("Add Staff"):

        try:
            cursor.execute("INSERT INTO staff VALUES(?)",(new_staff,))
            conn.commit()
            st.success("Staff Added")
        except:
            st.error("Staff already exists")

    st.subheader("Remove Staff")

    staff_list=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()

    remove=st.selectbox("Select Staff",staff_list)

    if st.button("Remove Staff"):

        cursor.execute("DELETE FROM staff WHERE name=?",(remove,))
        conn.commit()

        st.success("Staff Removed")

    st.subheader("Change Fuel Price")

    for f in fuel_price:

        new_price=st.number_input(f,value=float(fuel_price[f]))

        if st.button(f"Update {f}"):

            cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?",(new_price,f))
            conn.commit()

            st.success(f"{f} Price Updated")
