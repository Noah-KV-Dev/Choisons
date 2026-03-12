import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(page_title="Petrol Pump System", layout="wide")

# ---------------- DATABASE ----------------

conn = sqlite3.connect("petrol_system.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
date TEXT,
staff TEXT
)
""")

columns = {
"nozzle":"INTEGER",
"fuel":"TEXT",
"opening":"REAL",
"closing":"REAL",
"litres":"REAL",
"price":"REAL",
"total":"REAL",
"paytm":"REAL",
"sbi":"REAL",
"hppay":"REAL",
"advance":"REAL",
"creditor":"REAL",
"balance":"REAL",
"time_in":"TEXT",
"time_out":"TEXT",
"hours":"REAL"
}

cursor.execute("PRAGMA table_info(sales)")
existing = [i[1] for i in cursor.fetchall()]

for col,ctype in columns.items():
    if col not in existing:
        cursor.execute(f"ALTER TABLE sales ADD COLUMN {col} {ctype}")

cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT UNIQUE)")
cursor.execute("""
CREATE TABLE IF NOT EXISTS fuel_price(
fuel TEXT UNIQUE,
price REAL
)
""")

conn.commit()

# ---------------- DEFAULT FUELS ----------------

default_fuels={
"Petrol":100,
"Diesel":90,
"Power Petrol":105,
"Oil":120
}

for f,p in default_fuels.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES(?,?)",(f,p))

conn.commit()

fuel_df=pd.read_sql("SELECT * FROM fuel_price",conn)
fuel_price=dict(zip(fuel_df["fuel"],fuel_df["price"]))

# ---------------- SESSION ----------------

if "admin" not in st.session_state:
    st.session_state.admin=False

if "checklist_done" not in st.session_state:
    st.session_state.checklist_done=False

if "checklist_date" not in st.session_state:
    st.session_state.checklist_date=str(date.today())

if st.session_state.checklist_date!=str(date.today()):
    st.session_state.checklist_done=False
    st.session_state.checklist_date=str(date.today())

# ---------------- SIDEBAR ----------------

menu=["Sales Entry","Reports","Staff Daily Checklist"]

if st.session_state.admin:
    menu.append("Admin Controls")

page=st.sidebar.selectbox("Menu",menu)

# ---------------- ADMIN LOGIN ----------------

st.sidebar.markdown("---")
st.sidebar.subheader("Admin Access")

if not st.session_state.admin:

    password=st.sidebar.text_input("Password",type="password")

    if st.sidebar.button("Login"):
        if password=="admin786":
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
        st.error("Sales Blocked — Complete Staff Daily Checklist")
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

    # -------- NOZZLE --------

    nozzle=st.selectbox("Nozzle",list(range(1,13)))

    cursor.execute("""
    SELECT closing FROM sales
    WHERE nozzle=?
    ORDER BY rowid DESC LIMIT 1
    """,(nozzle,))

    last=cursor.fetchone()

    if last:
        opening_default=float(last[0])
    else:
        opening_default=0.0

    opening=st.number_input("Opening Meter",value=opening_default)

    closing=st.number_input("Closing Meter",0.0)

    litres=max(closing-opening,0)

    # -------- FUEL --------

    fuel=st.selectbox("Fuel Type",list(fuel_price.keys()))

    price=fuel_price[fuel]

    st.info(f"Fuel Price ₹ {price}")

    total=litres*price

    st.success(f"Litres {litres} | Amount ₹ {total}")

    # -------- PAYMENTS --------

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
        paytm,sbi,hppay,advance,creditor,balance,
        time_in,time_out,hours
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
        str(date.today()),staff,nozzle,fuel,opening,closing,
        litres,price,total,paytm,sbi,hppay,advance,
        creditor,balance,str(time_in),str(time_out),hours
        ))

        conn.commit()

        st.success("Entry Saved")

    # -------- SUMMARY --------

    st.markdown("---")
    st.subheader("Today Summary")

    df=pd.read_sql("SELECT * FROM sales",conn)

    today=df[df["date"]==str(date.today())]

    if len(today)>0:

        c1,c2,c3,c4=st.columns(4)

        c1.metric("Sales ₹",round(today["total"].sum(),2))
        c2.metric("Litres",round(today["litres"].sum(),2))
        c3.metric("Staff Hours",round(today["hours"].sum(),2))
        c4.metric("Balance Cash",round(today["balance"].sum(),2))

        st.subheader("Staff Wise Litre Graph")

        chart=today.groupby("staff")["litres"].sum()

        st.bar_chart(chart)

# ---------------- REPORTS ----------------

elif page=="Reports":

    st.title("Reports")

    report=st.selectbox("Report Type",[
    "Daily Report",
    "Monthly Report",
    "Staff Report",
    "Fuel Report",
    "Payment Summary"
    ])

    df=pd.read_sql("SELECT * FROM sales",conn)

    if report=="Daily Report":

        d=st.date_input("Date",date.today())

        r=df[df["date"]==str(d)]

        st.dataframe(r)

        st.bar_chart(r.groupby("staff")["litres"].sum())

    elif report=="Monthly Report":

        df["month"]=df["date"].str.slice(0,7)

        m=st.selectbox("Month",df["month"].unique())

        r=df[df["month"]==m]

        st.dataframe(r)

        st.bar_chart(r.groupby("staff")["litres"].sum())

    elif report=="Staff Report":

        r=df.groupby("staff")[["litres","total","hours"]].sum()

        st.dataframe(r)

    elif report=="Fuel Report":

        r=df.groupby("fuel")[["litres","total"]].sum()

        st.dataframe(r)

    elif report=="Payment Summary":

        st.write(df[["paytm","sbi","hppay","advance","creditor","balance"]].sum())

# ---------------- CHECKLIST ----------------

elif page=="Staff Daily Checklist":

    st.title("Staff Daily Checklist")

    checklist=[
    "Staff on time",
    "Proper uniform",
    "Check pump machine",
    "Show zero before fueling",
    "Customer engine off",
    "Safe fueling",
    "Correct payment",
    "No mobile near pump",
    "Report leakage",
    "Keep area clean",
    "Submit machine reading",
    "Proper shift handover"
    ]

    checks=[st.checkbox(i) for i in checklist]

    if st.button("Apply Checklist"):

        if all(checks):
            st.session_state.checklist_done=True
            st.success("Checklist Completed — Sales Enabled")
        else:
            st.error("Checklist incomplete")

# ---------------- ADMIN ----------------

elif page=="Admin Controls":

    st.title("Admin Controls")

    new_staff=st.text_input("Add Staff")

    if st.button("Add Staff"):

        try:
            cursor.execute("INSERT INTO staff VALUES(?)",(new_staff,))
            conn.commit()
            st.success("Staff Added")
        except:
            st.error("Staff exists")

    staff_list=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()

    if len(staff_list)>0:

        remove=st.selectbox("Remove Staff",staff_list)

        if st.button("Remove Staff"):

            cursor.execute("DELETE FROM staff WHERE name=?",(remove,))
            conn.commit()

            st.success("Staff Removed")

    st.subheader("Fuel Price Change")

    for f in fuel_price:

        new_price=st.number_input(f,value=float(fuel_price[f]))

        if st.button(f"Update {f}"):

            cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?",(new_price,f))
            conn.commit()

            st.success("Price Updated")
