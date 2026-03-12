import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_pump.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------- CREATE TABLES ----------------
def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        staff TEXT,
        nozzle INTEGER DEFAULT 1,
        fuel TEXT,
        opening REAL DEFAULT 0,
        closing REAL DEFAULT 0,
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

# ---------------- DEFAULT FUELS ----------------
default_fuels = {"Petrol":100,"Diesel":90,"Power Petrol":105,"Oil":120}
for f,p in default_fuels.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES(?,?)",(f,p))
conn.commit()
fuel_df = pd.read_sql("SELECT * FROM fuel_price",conn)
fuel_price = dict(zip(fuel_df["fuel"],fuel_df["price"]))

# ---------------- SESSION STATE ----------------
if "admin" not in st.session_state: st.session_state.admin=False

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

# ---------------- READ SALES ----------------
def read_sales():
    df = pd.read_sql("SELECT * FROM sales ORDER BY id DESC", conn)
    for col in ["opening","closing","litres","price","total","paytm","sbi","hppay","advance","creditor","balance","time_in","time_out","hours","nozzle"]:
        if col not in df.columns: df[col]=0
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    return df

# ---------------- SALES ENTRY ----------------
if page=="Sales Entry":
    st.title("Fuel Sales Entry")

    sale_date = st.date_input("Select Date", date.today())
    staff_list = pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
    if not staff_list:
        st.warning("Add staff first in Admin Panel")
        st.stop()
    staff = st.selectbox("Staff", staff_list)

    # Checklist check
    cursor.execute("SELECT completed FROM checklist WHERE date=? AND staff=?",(sale_date.strftime("%Y-%m-%d"),staff))
    result = cursor.fetchone()
    if not result or result[0]==0:
        st.error(f"⚠ Sales blocked for {staff}. Checklist not completed.")
        st.stop()

    # Duty times
    col1,col2 = st.columns(2)
    with col1: time_in = st.time_input("Duty IN", value=time(9,0))
    with col2: time_out = st.time_input("Duty OUT", value=time(18,0))
    t1 = datetime.combine(sale_date, time_in)
    t2 = datetime.combine(sale_date, time_out)
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

    # ULTRA RELIABLE SAVE
    if st.button("Save Entry"):
        try:
            # SQLite Insert (auto-save)
            cursor.execute("""
            INSERT INTO sales(date,staff,nozzle,fuel,opening,closing,litres,price,total,
            paytm,sbi,hppay,advance,creditor,balance,time_in,time_out,hours)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,(sale_date.strftime("%Y-%m-%d"),staff,nozzle_int,fuel,opening,closing,litres,price,total,
                 paytm,sbi,hppay,advance,creditor,balance,t1.strftime("%H:%M"),t2.strftime("%H:%M"),hours))
            conn.commit()
            st.success("Sales Entry Saved ✅ (Auto-saved in system)")
        except Exception as e:
            st.error(f"Error Saving Entry: {e}")

    # Today summary
    st.markdown("---")
    df_today = read_sales()
    today_sales = df_today[df_today["date"]==sale_date.strftime("%Y-%m-%d")]
    if not today_sales.empty:
        summary = today_sales.groupby("staff").agg(
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
        st.subheader(f"Staff Summary for {sale_date}")
        st.dataframe(summary,use_container_width=True)
        st.subheader("Staff Litre Graph")
        st.bar_chart(summary.set_index("staff")["Litres"])
    else:
        st.info("No sales entries for this date yet. ✅ All previous entries are now recognized.")

# ---------------- REPORTS ----------------
# ... You can keep Reports, Checklist, Admin Panel same as before ...
# Use read_sales() to ensure all previous entries load properly.
