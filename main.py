import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_pump.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT, staff TEXT, nozzle INTEGER, fuel TEXT,
opening REAL, closing REAL, litres REAL, price REAL, total REAL,
paytm REAL, sbi REAL, hppay REAL, advance REAL, creditor REAL, balance REAL,
time_in TEXT, time_out TEXT, hours REAL
)
""")
cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_price(fuel TEXT UNIQUE, price REAL)")
cursor.execute("CREATE TABLE IF NOT EXISTS checklist(date TEXT, staff TEXT, completed INTEGER, PRIMARY KEY(date,staff))")
conn.commit()

# Default fuel prices
default_fuels = {"Petrol":100,"Diesel":90,"Power Petrol":105,"Oil":120}
for f,p in default_fuels.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES(?,?)",(f,p))
conn.commit()
fuel_df = pd.read_sql("SELECT * FROM fuel_price",conn)
fuel_price = dict(zip(fuel_df["fuel"],fuel_df["price"]))

# ---------------- SESSION STATE ----------------
if "admin" not in st.session_state: st.session_state.admin=False
if "check_date" not in st.session_state: st.session_state.check_date=str(date.today())
if st.session_state.check_date != str(date.today()): st.session_state.check_date=str(date.today())

# ---------------- SIDEBAR ----------------
menu=["Sales Entry","Reports","Staff Daily Checklist"]
if st.session_state.admin: menu.append("Admin Panel")
page = st.sidebar.selectbox("Menu",menu)

# ---------------- ADMIN LOGIN ----------------
st.sidebar.markdown("---")
st.sidebar.subheader("Admin Login")
if not st.session_state.admin:
    pw = st.sidebar.text_input("Password",type="password")
    if st.sidebar.button("Login"):
        if pw=="admin786":
            st.session_state.admin=True
            st.experimental_rerun()
        else:
            st.sidebar.error("Wrong Password")
else:
    st.sidebar.success("Admin Logged In")
    if st.sidebar.button("Logout"):
        st.session_state.admin=False
        st.experimental_rerun()

# ---------------- SALES ENTRY ----------------
if page=="Sales Entry":
    st.title("Fuel Sales Entry")
    staff_list = pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
    if not staff_list:
        st.warning("Admin must add staff first")
        st.stop()
    staff = st.selectbox("Staff",staff_list)

    # Checklist validation
    cursor.execute("SELECT completed FROM checklist WHERE date=? AND staff=?",(str(date.today()),staff))
    result = cursor.fetchone()
    if not result or result[0]==0:
        st.error(f"⚠ Sales blocked for {staff}. Staff Daily Checklist not completed.")
        st.stop()

    # Duty times
    col1,col2 = st.columns(2)
    with col1: time_in = st.time_input("Duty IN", value=time(9,0))
    with col2: time_out = st.time_input("Duty OUT", value=time(18,0))
    t1 = datetime.combine(date.today(), time_in)
    t2 = datetime.combine(date.today(), time_out)
    hours = round((t2-t1).seconds/3600,2)
    st.info(f"Working Hours: {hours}")

    # Nozzle and opening meter
    nozzle = st.selectbox("Nozzle", list(range(1,13)))
    nozzle_int = int(nozzle)
    try:
        cursor.execute("SELECT closing FROM sales WHERE nozzle=? ORDER BY id DESC LIMIT 1",(nozzle_int,))
        last = cursor.fetchone()
        opening_default = float(last[0]) if last and last[0] is not None else 0.0
    except:
        opening_default = 0.0

    opening = st.number_input("Opening Meter", value=opening_default, step=0.01, format="%.2f")
    closing = st.number_input("Closing Meter",0.0, step=0.01, format="%.2f")
    litres = round(max(closing-opening,0),2)

    # Fuel selection
    fuel = st.selectbox("Fuel Type",list(fuel_price.keys()))
    price = float(fuel_price[fuel])
    st.info(f"Fuel Price ₹ {price}")
    total = round(litres*price,2)
    st.success(f"Litres {litres} | Amount ₹ {total}")

    # Payments
    st.subheader("Payments")
    paytm = st.number_input("Paytm",0.0, step=0.01)
    sbi = st.number_input("SBI",0.0, step=0.01)
    hppay = st.number_input("HP Pay",0.0, step=0.01)
    advance = st.number_input("Advance Paid",0.0, step=0.01)
    creditor = st.number_input("Creditor",0.0, step=0.01)
    balance = round(total-(paytm+sbi+hppay+advance+creditor),2)
    st.warning(f"Balance Cash ₹ {balance}")

    # ---------------- SAVE ENTRY ----------------
    if st.button("Save Entry"):
        try:
            cursor.execute("""
                INSERT INTO sales(
                date,staff,nozzle,fuel,opening,closing,litres,price,total,
                paytm,sbi,hppay,advance,creditor,balance,time_in,time_out,hours
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                str(date.today()), staff, nozzle_int, fuel, float(opening), float(closing),
                float(litres), float(price), float(total), float(paytm), float(sbi), float(hppay),
                float(advance), float(creditor), float(balance),
                t1.strftime("%H:%M"), t2.strftime("%H:%M"), float(hours)
            ))
            conn.commit()
            st.success("Entry Saved Successfully ✅")
        except Exception as e:
            st.error(f"Error Saving Entry: {e}")

    # ---------------- TODAY SUMMARY ----------------
    st.markdown("---")
    st.subheader("Today Staff Summary")
    df = pd.read_sql("SELECT * FROM sales",conn)
    today = df[df["date"]==str(date.today())]
    for col in ["opening","closing","litres","total","paytm","sbi","hppay","advance","creditor","balance","hours"]:
        if col not in today.columns: today[col]=0
    if not today.empty:
        summary = today.groupby("staff").agg(
            Opening=("opening","sum"),
            Closing=("closing","sum"),
            Litres=("litres","sum"),
            Sales=("total","sum"),
            Paytm=("paytm","sum"),
            SBI=("sbi","sum"),
            HPPay=("hppay","sum"),
            Advance=("advance","sum"),
            Creditor=("creditor","sum"),
            CashBalance=("balance","sum"),
            Hours=("hours","sum")
        ).reset_index()
        summary["Cash Short"]=summary["CashBalance"].apply(lambda x: abs(x) if x<0 else 0)
        summary["Cash Excess"]=summary["CashBalance"].apply(lambda x: x if x>0 else 0)
        st.dataframe(summary,use_container_width=True)
        st.subheader("Staff Litre Graph Today")
        st.bar_chart(summary.set_index("staff")["Litres"])
    else:
        st.info("No sales entries for today")
