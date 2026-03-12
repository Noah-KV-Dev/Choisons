import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="⛽ Choisons Petrol Pump", layout="wide")
st.title("⛽ Choisons Petrol Pump Management System")
st.info("""
*Contact Details*  

Phone: +91 8590304889  
Email: kvpnaseeh@gmail.com / choisonscalicut@gmail.com  

Created by Nazeeh
""")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_pump.db", check_same_thread=False)
cursor = conn.cursor()

# --- CREATE TABLES ---
def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, staff TEXT, nozzle INTEGER, fuel TEXT,
        opening REAL DEFAULT 0, closing REAL DEFAULT 0, litres REAL DEFAULT 0, price REAL DEFAULT 0, total REAL DEFAULT 0,
        paytm REAL DEFAULT 0, sbi REAL DEFAULT 0, hppay REAL DEFAULT 0, advance REAL DEFAULT 0, creditor REAL DEFAULT 0, balance REAL DEFAULT 0,
        time_in TEXT DEFAULT '00:00', time_out TEXT DEFAULT '00:00', hours REAL DEFAULT 0
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
            st.experimental_rerun()
        else:
            st.sidebar.error("Wrong Password")
else:
    st.sidebar.success("Admin Logged In")
    if st.sidebar.button("Logout"):
        st.session_state.admin=False
        st.experimental_rerun()

# ---------------- UTILITY ----------------
def read_sales():
    """Read sales table safely"""
    try:
        create_tables()  # ensure table exists
        df = pd.read_sql("SELECT * FROM sales ORDER BY id DESC", conn)
        # ensure all expected columns exist
        for col in ["opening","closing","litres","price","total","paytm","sbi","hppay","advance","creditor","balance","time_in","time_out","hours","nozzle"]:
            if col not in df.columns: df[col]=0
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        return df
    except Exception as e:
        st.error(f"Error reading sales: {e}")
        return pd.DataFrame(columns=["id","date","staff","nozzle","fuel","opening","closing","litres","price","total",
                                     "paytm","sbi","hppay","advance","creditor","balance","time_in","time_out","hours"])

# ---------------- SALES ENTRY ----------------
if page=="Sales Entry":
    st.title("Fuel Sales Entry")
    staff_list = pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
    if not staff_list: st.warning("Admin must add staff first"); st.stop()
    staff = st.selectbox("Staff",staff_list)

    # Checklist validation
    cursor.execute("SELECT completed FROM checklist WHERE date=? AND staff=?",(str(date.today()),staff))
    result = cursor.fetchone()
    if not result or result[0]==0:
        st.error(f"⚠ Sales blocked for {staff}. Staff Daily Checklist not completed."); st.stop()

    # Duty times
    col1,col2 = st.columns(2)
    with col1: time_in = st.time_input("Duty IN", value=time(9,0))
    with col2: time_out = st.time_input("Duty OUT", value=time(18,0))
    t1 = datetime.combine(date.today(), time_in)
    t2 = datetime.combine(date.today(), time_out)
    hours = round((t2-t1).seconds/3600,2)
    st.info(f"Working Hours: {hours}")

    # Nozzle & opening
    nozzle = st.selectbox("Nozzle", list(range(1,13)))
    nozzle_int = int(nozzle)
    try:
        cursor.execute("SELECT closing FROM sales WHERE nozzle=? ORDER BY id DESC LIMIT 1",(nozzle_int,))
        last = cursor.fetchone()
        opening_default = float(last[0]) if last and last[0] is not None else 0.0
    except: opening_default = 0.0
    opening = st.number_input("Opening Meter", value=opening_default)
    closing = st.number_input("Closing Meter",0.0)
    litres = round(max(closing-opening,0),2)

    # Fuel & payments
    fuel = st.selectbox("Fuel Type",list(fuel_price.keys()))
    price = float(fuel_price[fuel])
    total = round(litres*price,2)
    st.info(f"Litres {litres} | Amount ₹ {total}")

    st.subheader("Payments")
    paytm = st.number_input("Paytm",0.0)
    sbi = st.number_input("SBI",0.0)
    hppay = st.number_input("HP Pay",0.0)
    advance = st.number_input("Advance Paid",0.0)
    creditor = st.number_input("Creditor",0.0)
    balance = round(total-(paytm+sbi+hppay+advance+creditor),2)
    st.warning(f"Balance Cash ₹ {balance}")

    if st.button("Save Entry"):
        try:
            cursor.execute("""
            INSERT INTO sales(
            date,staff,nozzle,fuel,opening,closing,litres,price,total,
            paytm,sbi,hppay,advance,creditor,balance,time_in,time_out,hours
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,(
            str(date.today()),staff,nozzle_int,fuel,opening,closing,
            litres,price,total,paytm,sbi,hppay,advance,creditor,balance,
            t1.strftime("%H:%M"),t2.strftime("%H:%M"),hours
            ))
            conn.commit()
            st.success("Entry Saved ✅")
        except Exception as e:
            st.error(f"Error Saving Entry: {e}")

    # Today's summary
    st.markdown("---")
    st.subheader("Today Staff Summary")
    df = read_sales()
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
    df = read_sales()
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
    
    # --- Staff Management ---
    new_staff=st.text_input("Add Staff")
    if st.button("Add Staff"):
        try:
            cursor.execute("INSERT INTO staff VALUES(?)",(new_staff,))
            conn.commit()
            st.success("Staff Added ✅")
        except:
            st.error("Staff Already Exists ❌")
    staff_list=pd.read_sql("SELECT name FROM staff",conn)["name"].tolist()
    if staff_list:
        remove=st.selectbox("Remove Staff",staff_list)
        if st.button("Remove Staff"):
            cursor.execute("DELETE FROM staff WHERE name=?",(remove,))
            conn.commit()
            st.success("Staff Removed ✅")

    # --- Fuel Price Control ---
    st.subheader("Fuel Price Control")
    for f in fuel_price:
        new_price=st.number_input(f,value=float(fuel_price[f]))
        if st.button(f"Update {f}"):
            cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?",(new_price,f))
            conn.commit()
            st.success("Price Updated ✅")

    # --- Sales Edit/Delete ---
    st.subheader("Edit / Delete Sales Entry")
    sales_df = read_sales()
    if not sales_df.empty:
        selected_id = st.selectbox("Select Sale ID", sales_df["id"].tolist())
        record = sales_df[sales_df["id"]==selected_id].iloc[0]

        staff_edit = st.selectbox("Staff", staff_list, index=staff_list.index(record["staff"]))
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
