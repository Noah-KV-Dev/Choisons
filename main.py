import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(page_title="Petrol Pump Manager", layout="wide")

# ---------------- DATABASE ----------------

conn = sqlite3.connect("petrol_pump.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT,
staff TEXT,
nozzle INTEGER,
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
time_out TEXT,
hours REAL
)
""")

cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_price(fuel TEXT UNIQUE, price REAL)")

conn.commit()

# ---------------- DEFAULT FUELS ----------------

fuels={"Petrol":100,"Diesel":90,"Power Petrol":105,"Oil":120}

for f,p in fuels.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES(?,?)",(f,p))

conn.commit()

fuel_df=pd.read_sql("SELECT * FROM fuel_price",conn)
fuel_price=dict(zip(fuel_df["fuel"],fuel_df["price"]))

# ---------------- SESSION ----------------

if "admin" not in st.session_state:
    st.session_state.admin=False

if "checklist_done" not in st.session_state:
    st.session_state.checklist_done=False

if "check_date" not in st.session_state:
    st.session_state.check_date=str(date.today())

if st.session_state.check_date!=str(date.today()):
    st.session_state.checklist_done=False
    st.session_state.check_date=str(date.today())

# ---------------- SIDEBAR ----------------

menu=["Sales Entry","Reports","Staff Daily Checklist"]

if st.session_state.admin:
    menu.append("Admin Panel")

page=st.sidebar.selectbox("Menu",menu)

# ---------------- ADMIN LOGIN ----------------

st.sidebar.markdown("---")
st.sidebar.subheader("Admin Login")

if not st.session_state.admin:

    pw=st.sidebar.text_input("Password",type="password")

    if st.sidebar.button("Login"):
        if pw=="admin786":
            st.session_state.admin=True
            st.rerun()
        else:
            st.sidebar.error("Wrong Password")

else:

    st.sidebar.success("Admin Logged In")

    if st.sidebar.button("Logout"):
        st.session_state.admin=False
        st.rerun()

# ---------------- SALES ENTRY ----------------

if page=="Sales Entry":

    st.title("Fuel Sales Entry")

    if not st.session_state.checklist_done:
        st.error("Sales Entry Blocked — Checklist not completed")
        st.stop()

    staff_list=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()

    if len(staff_list)==0:
        st.warning("Admin must add staff first")
        st.stop()

    staff=st.selectbox("Staff",staff_list)

    c1,c2=st.columns(2)

    with c1:
        time_in=st.time_input("Duty IN")

    with c2:
        time_out=st.time_input("Duty OUT")

    t1=datetime.combine(date.today(),time_in)
    t2=datetime.combine(date.today(),time_out)

    hours=round((t2-t1).seconds/3600,2)

    st.info(f"Working Hours: {hours}")

    nozzle=st.selectbox("Nozzle",list(range(1,13)))

    cursor.execute("""
    SELECT closing FROM sales
    WHERE nozzle=?
    ORDER BY id DESC LIMIT 1
    """,(nozzle,))

    last=cursor.fetchone()

    if last:
        opening_default=float(last[0])
    else:
        opening_default=0.0

    opening=st.number_input("Opening Meter",value=opening_default)
    closing=st.number_input("Closing Meter",0.0)

    litres=max(closing-opening,0)

    fuel=st.selectbox("Fuel Type",list(fuel_price.keys()))
    price=fuel_price[fuel]

    st.info(f"Fuel Price ₹ {price}")

    total=litres*price

    st.success(f"Litres {litres} | Amount ₹ {total}")

    st.subheader("Payments")

    paytm=st.number_input("Paytm",0.0)
    sbi=st.number_input("SBI",0.0)
    hppay=st.number_input("HP Pay",0.0)
    advance=st.number_input("Advance Paid",0.0)
    creditor=st.number_input("Creditor",0.0)

    paid=paytm+sbi+hppay+advance+creditor

    balance=total-paid

    st.warning(f"Balance Cash ₹ {balance}")

    if st.button("Save Entry"):

        cursor.execute("""
        INSERT INTO sales(
        date,staff,nozzle,fuel,opening,closing,litres,price,total,
        paytm,sbi,hppay,advance,creditor,balance,time_in,time_out,hours
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
        str(date.today()),staff,nozzle,fuel,opening,closing,
        litres,price,total,paytm,sbi,hppay,advance,
        creditor,balance,str(time_in),str(time_out),hours
        ))

        conn.commit()

        st.success("Entry Saved")

# ---------------- REPORTS ----------------

elif page=="Reports":

    st.title("Reports")

    df=pd.read_sql("SELECT * FROM sales",conn)

    st.dataframe(df)

# ---------------- CHECKLIST ----------------

elif page=="Staff Daily Checklist":

    st.title("Staff Daily Checklist")

    checklist=[
    "Report on time in uniform",
    "Guide vehicles in queue",
    "Check pump machine",
    "Show zero before fueling",
    "Customer engine off",
    "Safe fueling",
    "Collect correct payment",
    "No mobile near pump",
    "Report leakage",
    "Keep area clean",
    "Submit machine reading",
    "Proper shift handover",
    "Sales Entry Allowed"
    ]

    checks=[st.checkbox(i) for i in checklist]

    if st.button("Apply Checklist"):

        if all(checks):
            st.session_state.checklist_done=True
            st.success("Checklist Completed — Sales Entry Enabled")
        else:
            st.error("Checklist incomplete — Sales blocked")

# ---------------- ADMIN PANEL ----------------

elif page=="Admin Panel":

    st.title("Admin Panel")

    new_staff=st.text_input("Add Staff")

    if st.button("Add Staff"):

        try:
            cursor.execute("INSERT INTO staff VALUES(?)",(new_staff,))
            conn.commit()
            st.success("Staff Added")
        except:
            st.error("Staff Exists")

    staff_list=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()

    if len(staff_list)>0:

        remove=st.selectbox("Remove Staff",staff_list)

        if st.button("Remove Staff"):

            cursor.execute("DELETE FROM staff WHERE name=?",(remove,))
            conn.commit()

            st.success("Staff Removed")

    st.subheader("Fuel Price Control")

    for f in fuel_price:

        new_price=st.number_input(f,value=float(fuel_price[f]))

        if st.button(f"Update {f}"):

            cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?",(new_price,f))
            conn.commit()

            st.success("Price Updated")

    # -------- EDIT SALES --------

    st.subheader("Edit Sales Data")

    df=pd.read_sql("SELECT * FROM sales",conn)

    if len(df)>0:

        edit_id=st.selectbox("Select Record ID",df["id"])

        row=df[df["id"]==edit_id].iloc[0]

        new_open=st.number_input("Opening",value=float(row["opening"]))
        new_close=st.number_input("Closing",value=float(row["closing"]))

        if st.button("Update Record"):

            litres=new_close-new_open
            total=litres*row["price"]

            cursor.execute("""
            UPDATE sales
            SET opening=?,closing=?,litres=?,total=?
            WHERE id=?
            """,(new_open,new_close,litres,total,edit_id))

            conn.commit()

            st.success("Record Updated")
