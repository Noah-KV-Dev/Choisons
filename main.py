import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(page_title="Petrol Pump Manager", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_pump.db", check_same_thread=False)
cursor = conn.cursor()

# SALES TABLE
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

# STAFF TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT UNIQUE)")

# FUEL PRICE TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_price(fuel TEXT UNIQUE, price REAL)")

# CHECKLIST TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS checklist(
date TEXT,
staff TEXT,
completed INTEGER,
PRIMARY KEY(date,staff)
)
""")

conn.commit()

# ---------------- DEFAULT FUELS ----------------
fuels = {"Petrol":100,"Diesel":90,"Power Petrol":105,"Oil":120}
for f,p in fuels.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_price VALUES(?,?)",(f,p))
conn.commit()
fuel_df = pd.read_sql("SELECT * FROM fuel_price",conn)
fuel_price = dict(zip(fuel_df["fuel"],fuel_df["price"]))

# ---------------- SESSION ----------------
if "admin" not in st.session_state: st.session_state.admin=False
if "check_date" not in st.session_state: st.session_state.check_date=str(date.today())
if st.session_state.check_date != str(date.today()):
    st.session_state.check_date=str(date.today())

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
    if len(staff_list)==0:
        st.warning("Admin must add staff first")
        st.stop()
    staff = st.selectbox("Staff",staff_list)

    # --- CHECK CHECKLIST ---
    cursor.execute("SELECT completed FROM checklist WHERE date=? AND staff=?",(str(date.today()),staff))
    result = cursor.fetchone()
    if not result or result[0]==0:
        st.error(f"⚠ Sales blocked for {staff}. Staff Daily Checklist not completed.")
        st.stop()

    # --- DUTY TIMES ---
    col1,col2 = st.columns(2)
    with col1: time_in = st.time_input("Duty IN")
    with col2: time_out = st.time_input("Duty OUT")
    t1 = datetime.combine(date.today(),time_in)
    t2 = datetime.combine(date.today(),time_out)
    hours = round((t2-t1).seconds/3600,2)
    st.info(f"Working Hours: {hours}")

    # --- NOZZLE / OPENING ---
    nozzle = st.selectbox("Nozzle",list(range(1,13)))
    cursor.execute("SELECT closing FROM sales WHERE nozzle=? ORDER BY id DESC LIMIT 1",(nozzle,))
    last = cursor.fetchone()
    opening_default = float(last[0]) if last else 0.0
    opening = st.number_input("Opening Meter",value=opening_default)
    closing = st.number_input("Closing Meter",0.0)
    litres = max(closing-opening,0)

    # --- FUEL ---
    fuel = st.selectbox("Fuel Type",list(fuel_price.keys()))
    price = fuel_price[fuel]
    st.info(f"Fuel Price ₹ {price}")
    total = litres*price
    st.success(f"Litres {litres} | Amount ₹ {total}")

    # --- PAYMENTS ---
    st.subheader("Payments")
    paytm = st.number_input("Paytm",0.0)
    sbi = st.number_input("SBI",0.0)
    hppay = st.number_input("HP Pay",0.0)
    advance = st.number_input("Advance Paid",0.0)
    creditor = st.number_input("Creditor",0.0)
    paid = paytm+sbi+hppay+advance+creditor
    balance = total - paid
    st.warning(f"Balance Cash ₹ {balance}")

    # --- SAVE ENTRY ---
    if st.button("Save Entry"):
        cursor.execute("""
        INSERT INTO sales(
        date,staff,nozzle,fuel,opening,closing,litres,price,total,
        paytm,sbi,hppay,advance,creditor,balance,time_in,time_out,hours
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
        str(date.today()),staff,nozzle,fuel,opening,closing,
        litres,price,total,paytm,sbi,hppay,advance,creditor,balance,
        str(time_in),str(time_out),hours
        ))
        conn.commit()
        st.success("Entry Saved")

    # --- TODAY SUMMARY ---
    st.markdown("---")
    st.subheader("Today Staff Summary")
    df = pd.read_sql("SELECT * FROM sales",conn)
    today = df[df["date"]==str(date.today())]
    if len(today)>0:
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
        summary["Cash Short"] = summary["CashBalance"].apply(lambda x: abs(x) if x<0 else 0)
        summary["Cash Excess"] = summary["CashBalance"].apply(lambda x: x if x>0 else 0)
        st.dataframe(summary,use_container_width=True)
        st.bar_chart(summary.set_index("staff")["Litres"])

# ---------------- REPORTS ----------------
elif page=="Reports":
    st.title("Reports")
    df = pd.read_sql("SELECT * FROM sales",conn)
    report = st.selectbox("Report Type",["Daily","Monthly"])
    if report=="Daily":
        d = st.date_input("Select Date",date.today())
        r = df[df["date"]==str(d)]
        st.dataframe(r)
    elif report=="Monthly":
        df["month"]=df["date"].str.slice(0,7)
        months = df["month"].unique()
        m = st.selectbox("Month",months)
        r = df[df["month"]==m]
        summary = r.groupby("staff").agg(
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
        summary["Cash Short"] = summary["CashBalance"].apply(lambda x: abs(x) if x<0 else 0)
        summary["Cash Excess"] = summary["CashBalance"].apply(lambda x: x if x>0 else 0)
        st.subheader("Monthly Staff Summary")
        st.dataframe(summary,use_container_width=True)
        st.subheader("Monthly Staff Litre Graph")
        st.bar_chart(summary.set_index("staff")["Litres"])

# ---------------- STAFF DAILY CHECKLIST ----------------
elif page=="Staff Daily Checklist":
    st.title("Staff Daily Checklist")
    staff_list = pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
    if len(staff_list)==0:
        st.warning("No staff available")
        st.stop()
    staff = st.selectbox("Select Staff",staff_list)
    checklist = [
        "Report on time in clean uniform with ID badge",
        "Guide vehicles to maintain queue",
        "Check pump machine condition",
        "Verify area is clean and hazard-free",
        "Confirm fire extinguisher location",
        "Show ZERO reading before fueling",
        "Ask customer to switch off engine",
        "Insert nozzle properly and fuel safely",
        "Stop exactly at requested amount",
        "Avoid fuel spoilage",
        "Collect correct payment",
        "Issue receipt when required",
        "No mobile phone near pump",
        "No smoking in forecourt",
        "Report leakage or machine fault",
        "Keep pump area clean",
        "Submit machine reading",
        "Hand over duty properly",
        "Sales Entry Allowed"
    ]
    checks = [st.checkbox(i) for i in checklist]
    if st.button("Apply Checklist"):
        if all(checks):
            cursor.execute("""
            INSERT OR REPLACE INTO checklist(date,staff,completed) VALUES(?,?,1)
            """,(str(date.today()),staff))
            conn.commit()
            st.success(f"Checklist completed for {staff}. Sales entry enabled.")
        else:
            st.error("Checklist incomplete. Sales entry will remain blocked.")

# ---------------- ADMIN PANEL ----------------
elif page=="Admin Panel":
    st.title("Admin Panel")
    new_staff = st.text_input("Add Staff")
    if st.button("Add Staff"):
        try:
            cursor.execute("INSERT INTO staff VALUES(?)",(new_staff,))
            conn.commit()
            st.success("Staff Added")
        except:
            st.error("Staff Exists")
    staff_list = pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
    if len(staff_list)>0:
        remove = st.selectbox("Remove Staff",staff_list)
        if st.button("Remove Staff"):
            cursor.execute("DELETE FROM staff WHERE name=?",(remove,))
            conn.commit()
            st.success("Staff Removed")
    st.subheader("Fuel Price Control")
    for f in fuel_price:
        new_price = st.number_input(f,value=float(fuel_price[f]))
        if st.button(f"Update {f}"):
            cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?",(new_price,f))
            conn.commit()
            st.success("Price Updated")
    # --- EDIT SALES ---
    st.subheader("Edit Sales Data")
    df = pd.read_sql("SELECT * FROM sales",conn)
    if len(df)>0:
        edit_id = st.selectbox("Select Record ID",df["id"])
        row = df[df["id"]==edit_id].iloc[0]
        new_open = st.number_input("Opening",value=float(row["opening"]))
        new_close = st.number_input("Closing",value=float(row["closing"]))
        if st.button("Update Record"):
            litres = new_close - new_open
            total = litres * row["price"]
            cursor.execute("""
            UPDATE sales
            SET opening=?,closing=?,litres=?,total=?
            WHERE id=?
            """,(new_open,new_close,litres,total,edit_id))
            conn.commit()
            st.success("Record Updated")
