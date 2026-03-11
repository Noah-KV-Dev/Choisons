import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# ---------------- THEME / STYLE ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');
html,body,[class*="css"]{
font-family:'Lexend',sans-serif;
color:black;
}
.stApp{
background-color:#ff6f00;
}
</style>
""", unsafe_allow_html=True)

st.title("⛽ Choisons Petrol Pump Management System")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_sales.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
date TEXT,
staff TEXT,
fuel TEXT,
nozzle TEXT,
opening REAL,
closing REAL,
litres REAL,
price REAL,
total REAL,
duty_in TEXT,
duty_out TEXT,
hours REAL
)
""")
cursor.execute("CREATE TABLE IF NOT EXISTS staff(name TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_price(fuel TEXT UNIQUE, price REAL)")
conn.commit()

# Default fuel prices
for f, p in [('Petrol',100), ('Diesel',90), ('Power Petrol',105)]:
    cursor.execute("INSERT OR IGNORE INTO fuel_price(fuel,price) VALUES (?,?)", (f,p))
conn.commit()

# Load data
df = pd.read_sql("SELECT rowid,* FROM sales", conn)
staff_df = pd.read_sql("SELECT * FROM staff", conn)
price_df = pd.read_sql("SELECT * FROM fuel_price", conn)
staff_list = staff_df["name"].tolist()
price_dict = dict(zip(price_df["fuel"], price_df["price"]))

# ---------------- CONTACT INFO ----------------
st.info("""
Phone: +91 8590304889  
Email: kvpnaseeh@gmail.com  
Created by Nazeeh
""")

# ---------------- ADMIN PANEL ----------------
st.sidebar.title("Admin Panel")
admin_user = "admin"
admin_pass = "admin123"
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged=False

username = st.sidebar.text_input("Username", key="admin_username")
password = st.sidebar.text_input("Password", type="password", key="admin_password")
if st.sidebar.button("Login", key="admin_login"):
    if username==admin_user and password==admin_pass:
        st.session_state.admin_logged=True
        st.sidebar.success("Admin Logged In")
    else:
        st.sidebar.error("Invalid Login")

if st.session_state.admin_logged:
    st.sidebar.success("Admin Mode Active")
    if st.sidebar.button("Logout", key="admin_logout"):
        st.session_state.admin_logged=False
        st.rerun()
    st.subheader("Admin Controls")

    # Add staff
    new_staff = st.text_input("Add Staff", key="add_staff_input")
    if st.button("Add Staff", key="add_staff_btn"):
        cursor.execute("INSERT INTO staff VALUES(?)", (new_staff,))
        conn.commit()
        st.success("Staff Added")
        st.rerun()

    # Delete record
    record_id = st.selectbox("Delete Record", df["rowid"], key="delete_record_select")
    if st.button("Delete Record", key="delete_record_btn"):
        cursor.execute("DELETE FROM sales WHERE rowid=?", (record_id,))
        conn.commit()
        st.warning("Record Deleted")
        st.rerun()

    # Delete all data
    if st.button("Delete All Data", key="delete_all_btn"):
        cursor.execute("DELETE FROM sales")
        conn.commit()
        st.error("All Data Deleted")
        st.rerun()

    # Admin fuel price change
    st.subheader("Admin Fuel Price Update")
    fuel_admin = st.selectbox("Select Fuel", ["Petrol","Diesel","Power Petrol"], key="admin_fuel_select")
    price_admin = st.number_input(f"Set Price for " + fuel_admin, min_value=0.0, value=price_dict.get(fuel_admin,0), key="admin_price_input")
    if price_admin != price_dict.get(fuel_admin):
        price_dict[fuel_admin] = price_admin
        cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?", (price_admin, fuel_admin))
        conn.commit()
        st.success(f"{fuel_admin} price updated to ₹{price_admin}")

# ---------------- STAFF SALES ENTRY ----------------
st.subheader("Sales Entry")
col1, col2, col3 = st.columns(3)
with col1:
    if len(staff_list)==0:
        st.warning("Admin must add staff first")
        staff=""
    else:
        staff = st.selectbox("Staff Name", staff_list, key="staff_select")
with col2:
    entry_date = st.date_input("Date", date.today(), key="date_entry")
with col3:
    # Show fuel price in selectbox
    fuel_display = [f"{f} (₹{price_dict[f]})" for f in ["Petrol","Diesel","Power Petrol"]]
    fuel_choice = st.selectbox("Fuel Type", fuel_display, key="fuel_select")
    fuel = fuel_choice.split(" ")[0]  # extract fuel name
price = price_dict.get(fuel,0)

# ---------------- NOZZLE AND METRES ----------------
nozzle = st.selectbox("Nozzle", 
                      ["Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4","Nozzle 5",
                       "Nozzle 6","Nozzle 7","Nozzle 8","Nozzle 9","Nozzle 10"], 
                      key="nozzle_select")

# Auto-open = last closing of this nozzle
last = pd.read_sql("SELECT closing FROM sales WHERE nozzle=? ORDER BY rowid DESC LIMIT 1",
                   conn, params=(nozzle,))
default_opening = float(last.iloc[0]["closing"]) if len(last)>0 else 0.0
col4, col5 = st.columns(2)
with col4:
    opening = st.number_input("Opening Metre", value=default_opening, key="opening")
with col5:
    closing = st.number_input("Closing Metre", min_value=0.0, key="closing")

# ---------------- DUTY HOURS ----------------
col6, col7 = st.columns(2)
with col6:
    duty_in = st.time_input("Duty IN", key="duty_in")
with col7:
    duty_out = st.time_input("Duty OUT", key="duty_out")
in_time = datetime.combine(date.today(), duty_in)
out_time = datetime.combine(date.today(), duty_out)
hours = max((out_time - in_time).total_seconds()/3600, 0)
st.info(f"Work Hours: {round(hours,2)} hrs")

# ---------------- VALIDATION ----------------
if closing < opening:
    st.error("Closing metre cannot be less than opening metre!")
    save_allowed = False
else:
    if len(last) > 0 and closing - last.iloc[0]["closing"] > 500:
        st.warning("Closing metre is unusually high compared to last closing metre!")
    save_allowed = True

# ---------------- CALCULATIONS ----------------
litres = max(closing - opening, 0)
total = litres * price
st.success(f"Litres Sold: {round(litres,2)} L")
st.success(f"Total Sale: ₹ {round(total,2)}")

# ---------------- SAVE ENTRY ----------------
if st.button("Save Entry", key="save_entry"):
    if staff=="":
        st.error("Add staff first")
    elif not save_allowed:
        st.error("Cannot save entry due to metre error.")
    else:
        cursor.execute("""
        INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (str(entry_date), staff, fuel, nozzle, opening, closing, litres, price, total,
              str(duty_in), str(duty_out), hours))
        conn.commit()
        st.success("Data Saved")
        st.rerun()

# ---------------- DAILY SUMMARY ----------------
st.subheader("DAILY SUMMARY")
df = pd.read_sql("SELECT rowid,* FROM sales", conn)
today = str(date.today())
daily_summary = df[df['date']==today].groupby(["staff","fuel"]).agg({
    "price":"first",
    "litres":"sum",
    "total":"sum",
    "hours":"sum"
}).reset_index()
st.dataframe(daily_summary)

# ---------------- DAILY STAFF SUMMARY ----------------
st.subheader("DAILY STAFF SUMMARY")
daily_staff_summary = df[df['date']==today].groupby(["staff"]).agg({
    "litres":"sum",
    "total":"sum",
    "hours":"sum"
}).reset_index()
st.dataframe(daily_staff_summary)

# ---------------- MONTHLY SUMMARY ----------------
st.subheader("MONTHLY SUMMARY")
df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
monthly_summary = df.groupby(['month','staff','fuel']).agg({
    "price":"first",
    'litres':'sum',
    'total':'sum',
    'hours':'sum'
}).reset_index()
monthly_summary['month'] = monthly_summary['month'].astype(str)
st.dataframe(monthly_summary)

# ---------------- MONTHLY STAFF SUMMARY ----------------
st.subheader("MONTHLY STAFF SUMMARY")
monthly_staff_summary = df.groupby(['month','staff']).agg({
    'litres':'sum',
    'total':'sum',
    'hours':'sum'
}).reset_index()
monthly_staff_summary['month'] = monthly_staff_summary['month'].astype(str)
st.dataframe(monthly_staff_summary)

# ---------------- STAFF SEARCH / SUMMARY ----------------
st.subheader("Staff Search / Summary")
if len(staff_list)>0:
    staff_search = st.selectbox("Select Staff to View Summary", staff_list, key="staff_search")
    
    # Daily for selected staff
    staff_daily = df[(df['date']==today) & (df['staff']==staff_search)]
    if not staff_daily.empty:
        st.markdown(f"**Daily Details for {staff_search}:**")
        st.dataframe(staff_daily)
    else:
        st.info(f"No sales today for {staff_search}")
    
    # Monthly for selected staff
    staff_month = df[df['staff']==staff_search].groupby(['month','fuel']).agg({
        'litres':'sum',
        'total':'sum',
        'hours':'sum'
    }).reset_index()
    if not staff_month.empty:
        st.markdown(f"**Monthly Summary for {staff_search}:**")
        st.dataframe(staff_month)
    else:
        st.info(f"No monthly records for {staff_search}")
