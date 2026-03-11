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

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff(
name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fuel_price(
fuel TEXT,
price REAL
)
""")
conn.commit()

# Default fuel prices
cursor.execute("SELECT COUNT(*) FROM fuel_price")
if cursor.fetchone()[0]==0:
    cursor.execute("INSERT INTO fuel_price VALUES('Petrol',100)")
    cursor.execute("INSERT INTO fuel_price VALUES('Diesel',90)")
    cursor.execute("INSERT INTO fuel_price VALUES('Power Petrol',105)")
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
    fuel = st.selectbox("Fuel Type", ["Petrol","Diesel","Power Petrol"], key="fuel_select")

# ---------------- FUEL PRICE CHANGE FOR STAFF ----------------
st.subheader("Fuel Price Override (Optional)")
colp1, colp2 = st.columns([2,1])
with colp1:
    fuel_price_override = st.number_input(f"Set {fuel} Price (Leave blank for default)", 
                                          min_value=0.0, value=price_dict.get(fuel,0), key="fuel_override")
with colp2:
    if st.button("Update Price for This Entry", key="update_price_staff"):
        price_dict[fuel] = fuel_price_override
        cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?", (fuel_price_override,fuel))
        conn.commit()
        st.success(f"{fuel} price updated to ₹{fuel_price_override}")

# ---------------- NOZZLE AND METRES ----------------
nozzle = st.selectbox("Nozzle", 
                      ["Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4","Nozzle 5",
                       "Nozzle 6","Nozzle 7","Nozzle 8","Nozzle 9","Nozzle 10"], 
                      key="nozzle_select")

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

# ---------------- CALCULATIONS ----------------
litres = max(closing - opening, 0)
price = price_dict.get(fuel, 0)
total = litres * price
st.success(f"Litres Sold: {round(litres,2)} L")
st.success(f"Total Sale: ₹ {round(total,2)}")

# ---------------- SAVE ENTRY ----------------
if st.button("Save Entry", key="save_entry"):
    if staff=="":
        st.error("Add staff first")
    else:
        cursor.execute("""
        INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (str(entry_date), staff, fuel, nozzle, opening, closing, litres, price, total,
              str(duty_in), str(duty_out), hours))
        conn.commit()
        st.success("Data Saved")
        st.rerun()

# ---------------- DATA TABLES AND SUMMARIES ----------------
st.subheader("Sales Records")
df = pd.read_sql("SELECT rowid,* FROM sales", conn)
st.dataframe(df,use_container_width=True)

# Daily summary
st.subheader("Daily Sales Summary")
today_data = df[df["date"]==str(date.today())]
st.metric("Litres Today", round(today_data["litres"].sum(),2))
st.metric("Sales Today", round(today_data["total"].sum(),2))

# Staff litres and hours
st.subheader("Staff Total Litres")
staff_litres = df.groupby("staff")["litres"].sum().reset_index()
st.dataframe(staff_litres)

st.subheader("Staff Total Hours")
staff_hours = df.groupby("staff")["hours"].sum().reset_index()
st.dataframe(staff_hours)

# Nozzle sales
st.subheader("Nozzle Sales")
nozzle_sales = df.groupby("nozzle")["litres"].sum().reset_index()
st.dataframe(nozzle_sales)

# ---------------- MONTHLY SUMMARY PER STAFF ----------------
st.subheader("Monthly Summary Per Staff")
df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
monthly_summary = df.groupby(['month','staff']).agg({
    'litres':'sum',
    'total':'sum',
    'hours':'sum'
}).reset_index()
st.dataframe(monthly_summary)

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
    cola, colb = st.columns(2)
    with cola:
        fuel_admin = st.selectbox("Select Fuel", ["Petrol","Diesel","Power Petrol"], key="admin_fuel_select")
    with colb:
        price_admin = st.number_input(f"Set {fuel_admin} Price", min_value=0.0, key="admin_price_input")
    if st.button("Update Fuel Price", key="admin_update_price"):
        cursor.execute("UPDATE fuel_price SET price=? WHERE fuel=?", (price_admin, fuel_admin))
        conn.commit()
        price_dict[fuel_admin] = price_admin
        st.success(f"{fuel_admin} price updated to ₹{price_admin}")
