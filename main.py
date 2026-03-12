import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

# ---------------- PAGE ----------------
st.set_page_config(page_title="Petrol Pump System", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_pump.db", check_same_thread=False)
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
conn.commit()

# ---------------- CHECKLIST ----------------

CHECKLIST_ITEMS = [

"Report on time in clean uniform with ID badge",
"Before Duty Starts * Report on time in clean uniform with ID badge",
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
"Report leakage, smell, or machine fault immediately",
"Do not argue with customers — call manager",
"Follow all safety procedures of Hindustan Petroleum",

"Keep pump area clean",
"Report machine reading to manager",
"Submit any pending receipts or issues",
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

# ---------------- ADMIN ----------------

if "admin" not in st.session_state:
    st.session_state.admin=False

st.sidebar.title("Admin")

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

    st.title("Fuel Entry")

    if not st.session_state.checklist_applied:

        missing=[k for k,v in st.session_state.checklist_state.items() if not v]

        if missing:
            st.error("Sales Blocked. Complete Staff Daily Checklist first.")
            st.write("Missing Items:")
            for m in missing:
                st.write("-",m)

            st.stop()

    staff_list=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()

    staff=st.selectbox("Staff",staff_list)

    fuel=st.selectbox("Fuel",["Petrol","Diesel"])

    opening=st.number_input("Opening Meter",0.0)

    closing=st.number_input("Closing Meter",0.0)

    price=st.number_input("Fuel Price",100.0)

    litres=max(closing-opening,0)

    total=litres*price

    st.info(f"Litres {litres} | Amount ₹ {total}")

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

        st.subheader("Daily Report")

        day=st.date_input("Date",date.today())

        daily=df[df["date"]==str(day)]

        if not daily.empty:

            daily=daily.sort_values("staff")

            st.dataframe(daily)

            st.write("Total Sales ₹",daily["total"].sum())

        st.subheader("Fuel Sales Chart")

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
