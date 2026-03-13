import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_pump.db", check_same_thread=False)
cursor = conn.cursor()

# Tables
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

# Default fuels
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

# Admin login/logout below menu
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

    # Checklist check
    cursor.execute("SELECT completed FROM checklist WHERE date=? AND staff=?",(str(date.today()),staff))
    result = cursor.fetchone()
    if not result or result[0]==0:
        st.error(f"⚠ Sales blocked for {staff}. Staff Daily Checklist not completed.")
        st.stop()

    # Duty times
    col1,col2 = st.columns(2)
    with col1: time_in = st.time_input("Duty IN")
    with col2: time_out = st.time_input("Duty OUT")
    t1 = datetime.combine(date.today(),time_in)
    t2 = datetime.combine(date.today(),time_out)
    hours = round((t2-t1).seconds/3600,2)
    st.info(f"Working Hours: {hours}")

    st.markdown("---")
    st.subheader("Multiple Nozzle Entry")
    if "multi_entries" not in st.session_state: 
        st.session_state.multi_entries=[{}]

    # Top buttons: Add new row & Remove last row
    col_add,col_remove = st.columns([1,1])
    with col_add:
        if st.button("Add Nozzle Entry"):
            st.session_state.multi_entries.append({})
    with col_remove:
        if st.button("Remove Last Entry") and st.session_state.multi_entries:
            st.session_state.multi_entries.pop(-1)

    total_amount=0

    for i, entry in enumerate(st.session_state.multi_entries):
        # Column widths: Nozzle=0.9, Fuel=1.2, Opening=2, Closing=2, Litres=0.5, Amount=0.9
        cols = st.columns([0.5,1.2,2,2,0.5,0.9])
        
        # Nozzle
        entry["nozzle"] = cols[0].number_input(
            f"Nozzle {i+1}", min_value=1, max_value=12,
            value=entry.get("nozzle",1), key=f"nozzle_{i}"
        )
        # Fuel
        entry["fuel"] = cols[1].selectbox(
            "", list(fuel_price.keys()), index=list(fuel_price.keys()).index(entry.get("fuel","Petrol")), key=f"fuel_{i}"
        )
        # Opening
        try:
            cursor.execute("SELECT closing FROM sales WHERE nozzle=? ORDER BY id DESC LIMIT 1",(entry["nozzle"],))
            last = cursor.fetchone()
            default_opening = float(last[0]) if last else 0.0
        except:
            default_opening=0.0
        entry["opening"] = cols[2].number_input(
            "", value=entry.get("opening",default_opening), key=f"opening_{i}", format="%.2f"
        )
        # Closing
        entry["closing"] = cols[3].number_input(
            "", value=entry.get("closing",entry.get("opening",default_opening)), key=f"closing_{i}", format="%.2f"
        )
        # Litres (font size 15px)
        entry["litres"] = max(entry["closing"]-entry["opening"],0)
        cols[4].markdown(f"<p style='font-size:15px;margin:0'>{entry['litres']:.2f}</p>", unsafe_allow_html=True)
        # Amount (font size 15px)
        entry["price"] = fuel_price[entry["fuel"]]
        entry["total"] = round(entry["litres"]*entry["price"],2)
        cols[5].markdown(f"<p style='font-size:15px;margin:0'>₹ {entry['total']:.2f}</p>", unsafe_allow_html=True)

        total_amount += entry["total"]

    st.info(f"Grand Total Amount: ₹ {total_amount}")

    # Payments
    st.subheader("Payments")
    paytm = st.number_input("Paytm",0.0)
    sbi = st.number_input("SBI",0.0)
    hppay = st.number_input("HP Pay",0.0)
    advance = st.number_input("Advance Paid",0.0)
    creditor = st.number_input("Creditor",0.0)
    balance = total_amount-(paytm+sbi+hppay+advance+creditor)
    st.warning(f"Balance Cash ₹ {balance}")

    if st.button("Save All Entries"):
        for entry in st.session_state.multi_entries:
            cursor.execute("""
            INSERT INTO sales(
            date,staff,nozzle,fuel,opening,closing,litres,price,total,
            paytm,sbi,hppay,advance,creditor,balance,time_in,time_out,hours
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,(
            str(date.today()),staff,entry["nozzle"],entry["fuel"],entry["opening"],entry["closing"],
            entry["litres"],entry["price"],entry["total"],
            paytm,sbi,hppay,advance,creditor,balance,
            time_in.strftime("%H:%M"),time_out.strftime("%H:%M"),hours
            ))
        conn.commit()
        st.success("All Entries Saved")
        st.session_state.multi_entries=[{}]  # reset entries










    # Today summary
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

# ---------------- REPORTS ----------------
elif page=="Reports":
    st.title("Reports")
    df = pd.read_sql("SELECT * FROM sales",conn)
    for col in ["opening","closing","litres","total","paytm","sbi","hppay","advance","creditor","balance","hours"]:
        if col not in df.columns: df[col]=0
    report_type = st.selectbox("Report Type",["Daily","Monthly"])
    if report_type=="Daily":
        d = st.date_input("Select Date",date.today())
        r = df[df["date"]==str(d)]
        st.dataframe(r)
        if not r.empty:
            daily_summary=r.groupby("staff").agg(Litres=("litres","sum"),Sales=("total","sum"),Hours=("hours","sum")).reset_index()
            st.bar_chart(daily_summary.set_index("staff")["Litres"])
    else:
        df["month"]=df["date"].str.slice(0,7)
        months=df["month"].unique()
        m=st.selectbox("Month",months)
        r=df[df["month"]==m]
        st.dataframe(r)
        if not r.empty:
            monthly_summary=r.groupby("staff").agg(Litres=("litres","sum"),Sales=("total","sum"),Hours=("hours","sum")).reset_index()
            st.bar_chart(monthly_summary.set_index("staff")["Litres"])

# ---------------- STAFF DAILY CHECKLIST ----------------
elif page=="Staff Daily Checklist":
    st.title("Staff Daily Checklist")
    staff_list = pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
    if not staff_list: st.warning("No staff available"); st.stop()
    staff = st.selectbox("Select Staff",staff_list)
    checklist_items=[
        "Report on time in clean uniform with ID badge","Guide vehicles to maintain queue",
        "Check pump machine condition","Verify area is clean and hazard-free",
        "Confirm fire extinguisher location","Show ZERO reading before fueling",
        "Ask customer to switch off engine","Insert nozzle properly and fuel safely",
        "Stop exactly at requested amount","Avoid fuel spoilage","Collect correct payment",
        "Issue receipt when required","No mobile phone near pump","No smoking in forecourt",
        "Report leakage or machine fault","Keep pump area clean","Submit machine reading",
        "Hand over duty properly","Sales Entry Allowed"
    ]
    checks=[st.checkbox(i) for i in checklist_items]
    if st.button("Apply Checklist"):
        if all(checks):
            cursor.execute("INSERT OR REPLACE INTO checklist(date,staff,completed) VALUES(?,?,1)",(str(date.today()),staff))
            conn.commit()
            st.success(f"Checklist completed for {staff}. Sales entry enabled.")
        else: st.error("Checklist incomplete. Sales entry will remain blocked.")

# ---------------- ADMIN PANEL ----------------
elif page=="Admin Panel":
    st.title("Admin Panel")
    new_staff=st.text_input("Add Staff")
    if st.button("Add Staff"):
        try:
            cursor.execute("INSERT INTO staff VALUES(?)",(new_staff,))
            conn.commit()
            st.success("Staff Added")
        except: st.error("Staff Exists")
    staff_list=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
    if staff_list:
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
