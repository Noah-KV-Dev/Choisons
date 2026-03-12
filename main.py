import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_pump.db", check_same_thread=False)
cursor = conn.cursor()

# --- CREATE OR FIX TABLES ---
def create_tables():
    # Base table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        staff TEXT,
        opening REAL DEFAULT 0,
        closing REAL DEFAULT 0,
        fuel TEXT,
        nozzle INTEGER DEFAULT 1,
        litres REAL DEFAULT 0,
        price REAL DEFAULT 0,
        total REAL DEFAULT 0,
        paytm REAL DEFAULT 0,
        sbi REAL DEFAULT 0,
        hppay REAL DEFAULT 0,
        advance REAL DEFAULT 0,
        creditor REAL DEFAULT 0,
        balance REAL DEFAULT 0,
        time_in TEXT DEFAULT '00:00',
        time_out TEXT DEFAULT '00:00',
        hours REAL DEFAULT 0
    )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS fuel_price(fuel TEXT UNIQUE, price REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS checklist(date TEXT, staff TEXT, completed INTEGER, PRIMARY KEY(date,staff))")
    conn.commit()

create_tables()

# --- DEFAULT FUELS ---
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
            st.success("Admin Logged In ✅")
        else:
            st.sidebar.error("Wrong Password")
else:
    st.sidebar.success("Admin Logged In")
    if st.sidebar.button("Logout"):
        st.session_state.admin=False
        st.success("Logged Out ✅")

# ---------------- UTILITY TO READ SALES SAFELY ----------------
def read_sales():
    try:
        df = pd.read_sql("SELECT * FROM sales ORDER BY id DESC", conn)
        # Ensure all columns exist
        for col in ["opening","closing","litres","price","total","paytm","sbi","hppay","advance","creditor","balance","time_in","time_out","hours","nozzle"]:
            if col not in df.columns:
                df[col]=0
        return df
    except:
        create_tables()
        return pd.DataFrame(columns=["id","date","staff","nozzle","fuel","opening","closing","litres","price","total","paytm","sbi","hppay","advance","creditor","balance","time_in","time_out","hours"])

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

    # Nozzle and opening
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

    # Fuel and payments
    fuel = st.selectbox("Fuel Type",list(fuel_price.keys()))
    price = float(fuel_price[fuel])
    total = round(litres*price,2)
    st.info(f"Litres {litres} | Amount ₹ {total}")

    paytm = float(st.number_input("Paytm",0.0, step=0.01))
    sbi = float(st.number_input("SBI",0.0, step=0.01))
    hppay = float(st.number_input("HP Pay",0.0, step=0.01))
    advance = float(st.number_input("Advance Paid",0.0, step=0.01))
    creditor = float(st.number_input("Creditor",0.0, step=0.01))
    balance = round(total-(paytm+sbi+hppay+advance+creditor),2)
    st.warning(f"Balance Cash ₹ {balance}")

    if st.button("Save Entry"):
        try:
            cursor.execute("""
            INSERT INTO sales(date,staff,nozzle,fuel,opening,closing,litres,price,total,
            paytm,sbi,hppay,advance,creditor,balance,time_in,time_out,hours)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,(str(date.today()),staff,nozzle_int,fuel,opening,closing,litres,price,total,
                 paytm,sbi,hppay,advance,creditor,balance,t1.strftime("%H:%M"),t2.strftime("%H:%M"),hours))
            conn.commit()
            st.success("Sales Entry Saved ✅")
        except Exception as e:
            st.error(f"Error Saving Entry: {e}")

# ---------------- ADMIN PANEL (Edit/Delete) ----------------
elif page=="Admin Panel":
    st.title("Admin Panel")

    # Read sales safely
    sales_df = read_sales()
    if not sales_df.empty:
        selected_id = st.selectbox("Select Sale ID", sales_df["id"].tolist())
        record = sales_df[sales_df["id"]==selected_id].iloc[0]

        staff_edit = st.selectbox("Staff", pd.read_sql("SELECT name FROM staff",conn)["name"].tolist(),
                                  index=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist().index(record["staff"]))
        fuel_edit = st.selectbox("Fuel", list(fuel_price.keys()), index=list(fuel_price.keys()).index(record["fuel"]))
        nozzle_edit = st.number_input("Nozzle", value=int(record["nozzle"]), min_value=1, max_value=12)
        opening_edit = st.number_input("Opening", value=float(record["opening"]))
        closing_edit = st.number_input("Closing", value=float(record["closing"]))
        litres_edit = round(max(closing_edit-opening_edit,0),2)
        price_edit = float(fuel_price[fuel_edit])
        total_edit = round(litres_edit*price_edit,2)
        paytm_edit = st.number_input("Paytm", value=float(record["paytm"]))
        sbi_edit = st.number_input("SBI", value=float(record["sbi"]))
        hppay_edit = st.number_input("HP Pay", value=float(record["hppay"]))
        advance_edit = st.number_input("Advance", value=float(record["advance"]))
        creditor_edit = st.number_input("Creditor", value=float(record["creditor"]))
        balance_edit = round(total_edit-(paytm_edit+sbi_edit+hppay_edit+advance_edit+creditor_edit),2)
        st.warning(f"Balance Cash ₹ {balance_edit}")

        if st.button("Update Sale"):
            cursor.execute("""
                UPDATE sales SET staff=?, fuel=?, nozzle=?, opening=?, closing=?, litres=?, price=?, total=?,
                paytm=?, sbi=?, hppay=?, advance=?, creditor=?, balance=? WHERE id=?
            """,(staff_edit,fuel_edit,nozzle_edit,opening_edit,closing_edit,litres_edit,price_edit,total_edit,
                 paytm_edit,sbi_edit,hppay_edit,advance_edit,creditor_edit,balance_edit,selected_id))
            conn.commit()
            st.success("Sale Updated ✅")

        if st.button("Delete Sale"):
            cursor.execute("DELETE FROM sales WHERE id=?",(selected_id,))
            conn.commit()
            st.success("Sale Deleted ✅")
