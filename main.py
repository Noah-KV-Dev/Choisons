import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import socket

# ---------------- MODE ----------------
mode = st.sidebar.radio("Mode", ["Offline", "Online"])
if mode == "Offline":
    conn = sqlite3.connect("petrol_sales.db", check_same_thread=False)
else:
    conn = sqlite3.connect("/tmp/petrol_sales.db", check_same_thread=False)

cursor = conn.cursor()

# ---------------- TABLES ----------------
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
    hours REAL,
    website_type TEXT,
    ip_address TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")
conn.commit()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# ---------------- STYLE ----------------
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

# ---------------- TITLE & CONTACT ----------------
st.title("⛽ Choisons Petrol Pump Management System")
st.info("""
**Contact Details**  

Phone: +91 8590304889  
Email: kvpnaseeh@gmail.com / choisonscalicut@gmail.com  

Created by Nazeeh
""")

# ---------------- FUEL PRICES ----------------
st.subheader("Fuel Prices")
col1, col2, col3 = st.columns(3)
with col1: petrol_price = st.number_input("Petrol Price", value=100.0)
with col2: diesel_price = st.number_input("Diesel Price", value=90.0)
with col3: power_price = st.number_input("Power Petrol Price", value=105.0)

# ---------------- STAFF DUTY ----------------
st.subheader("Staff Duty Time")
col4, col5 = st.columns(2)
with col4: duty_in = st.time_input("Duty IN")
with col5: duty_out = st.time_input("Duty OUT")
in_time = datetime.combine(date.today(), duty_in)
out_time = datetime.combine(date.today(), duty_out)
hours = max((out_time - in_time).total_seconds() / 3600, 0)
st.info(f"Work Hours: {round(hours,2)} hrs")

# ---------------- SALES ENTRY ----------------
st.subheader("Sales Entry")
col6, col7, col8 = st.columns(3)

# Staff list from DB
staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()
if not staff_list: staff_list = ["Add Staff in Admin Panel"]
with col6: staff = st.selectbox("Staff Name", staff_list)
with col7: entry_date = st.date_input("Date", date.today())
with col8: fuel = st.selectbox("Fuel Type", ["Petrol","Diesel","Power Petrol"])

nozzle = st.selectbox(
    "Nozzle",
    ["Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4","Nozzle 5",
     "Nozzle 6","Nozzle 7","Nozzle 8","Nozzle 9","Nozzle 10"]
)

col9, col10 = st.columns(2)
with col9: opening = st.number_input("Opening Metre")
with col10: closing = st.number_input("Closing Metre")

litres = max(closing - opening, 0)
price = petrol_price if fuel=="Petrol" else diesel_price if fuel=="Diesel" else power_price
total = litres * price

st.success(f"Litres Sold: {round(litres,2)} L")
st.success(f"Total Sale: ₹ {round(total,2)}")

website_type = mode
ip_address = socket.gethostbyname(socket.gethostname())

if st.button("Save Entry"):
    cursor.execute("""
    INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        str(entry_date), staff, fuel, nozzle, opening, closing,
        litres, price, total, str(duty_in), str(duty_out),
        hours, website_type, ip_address
    ))
    conn.commit()
    st.success("Data Saved")
    st.experimental_rerun()

# ---------------- LOAD DATA ----------------
df = pd.read_sql("SELECT rowid,* FROM sales", conn)

# ---------------- DATA TABLE ----------------
st.subheader("Sales Records")
st.dataframe(df, use_container_width=True)

# ---------------- DAILY SALES ----------------
st.subheader("Daily Sales Summary")
today_data = df[df["date"]==str(date.today())]
st.metric("Litres Today", round(today_data["litres"].sum(),2))
st.metric("Sales Today", round(today_data["total"].sum(),2))

# ---------------- STAFF LITRES ----------------
st.subheader("Monthly Litre Sales Per Staff")
staff_litres = df.groupby("staff")["litres"].sum().reset_index()
st.dataframe(staff_litres)

# ---------------- STAFF HOURS ----------------
st.subheader("Monthly Staff Working Hours")
staff_hours = df.groupby("staff")["hours"].sum().reset_index()
st.dataframe(staff_hours)

# ---------------- NOZZLE SALES ----------------
st.subheader("Nozzle Sales")
nozzle_sales = df.groupby("nozzle")["litres"].sum().reset_index()
st.dataframe(nozzle_sales)

# ---------------- ADMIN LOGIN ----------------
st.sidebar.title("Admin Panel")
admin_user = "admin"
admin_pass = "admin123"
if "admin_logged" not in st.session_state: st.session_state.admin_logged=False

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username==admin_user and password==admin_pass:
        st.session_state.admin_logged=True
        st.sidebar.success("Admin Logged In")
    else:
        st.sidebar.error("Invalid Login")

# ---------------- ADMIN CONTROLS ----------------
if st.session_state.admin_logged:
    st.sidebar.success("Admin Mode Active")
    if st.sidebar.button("Logout"):
        st.session_state.admin_logged=False
        st.experimental_rerun()

    st.subheader("⚠ Admin Controls")

    # Delete Record
    record_id = st.selectbox("Select Record ID to Delete", df["rowid"], key="del_id")
    if st.button("Delete Selected Record"): 
        cursor.execute("DELETE FROM sales WHERE rowid=?", (record_id,))
        conn.commit()
        st.warning("Record Deleted")
        st.experimental_rerun()

    if st.button("Delete All Data"):
        cursor.execute("DELETE FROM sales")
        conn.commit()
        st.error("All Data Deleted")
        st.experimental_rerun()

    # Update Fuel Prices
    st.subheader("Update Fuel Prices")
    fuel_to_update = st.selectbox("Select Fuel Type", ["Petrol","Diesel","Power Petrol"], key="fuel_update")
    new_price = st.number_input("New Price", min_value=0.0, value=100.0, step=0.5, key="new_price")
    if st.button("Update Fuel Price in All Records"):
        cursor.execute("UPDATE sales SET price=?, total=litres*? WHERE fuel=?", (new_price, new_price, fuel_to_update))
        conn.commit()
        st.success(f"Updated all {fuel_to_update} entries with price ₹{new_price}")
        st.experimental_rerun()

    # Add New Staff
    st.subheader("Add New Staff")
    new_staff = st.text_input("Staff Name", key="new_staff")
    if st.button("Add Staff"):
        if new_staff.strip() != "":
            try:
                cursor.execute("INSERT INTO staff(name) VALUES (?)", (new_staff.strip(),))
                conn.commit()
                st.success(f"Staff '{new_staff}' added")
            except sqlite3.IntegrityError:
                st.error("Staff already exists")
            st.experimental_rerun()
    staff_df = pd.read_sql("SELECT * FROM staff", conn)
    st.dataframe(staff_df)

    # Edit Existing Record
    st.subheader("Edit Existing Record")
    edit_record_id = st.selectbox("Select Record ID to Edit", df["rowid"], key="edit_id")
    record_to_edit = df[df["rowid"]==edit_record_id].iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        edit_staff = st.selectbox("Staff", staff_list, index=staff_list.index(record_to_edit["staff"]), key="edit_staff")
    with col2:
        edit_date = st.date_input("Date", pd.to_datetime(record_to_edit["date"]), key="edit_date")
    with col3:
        edit_fuel = st.selectbox("Fuel", ["Petrol","Diesel","Power Petrol"], index=["Petrol","Diesel","Power Petrol"].index(record_to_edit["fuel"]), key="edit_fuel")

    edit_nozzle = st.selectbox(
        "Nozzle",
        ["Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4","Nozzle 5",
         "Nozzle 6","Nozzle 7","Nozzle 8","Nozzle 9","Nozzle 10"],
        index=int(record_to_edit["nozzle"].split(" ")[1])-1,
        key="edit_nozzle"
    )

    col4, col5 = st.columns(2)
    with col4: edit_opening = st.number_input("Opening Metre", value=record_to_edit["opening"], key="edit_opening")
    with col5: edit_closing = st.number_input("Closing Metre", value=record_to_edit["closing"], key="edit_closing")

    edit_litres = max(edit_closing - edit_opening, 0)
    edit_price = petrol_price if edit_fuel=="Petrol" else diesel_price if edit_fuel=="Diesel" else power_price
    edit_total = edit_litres * edit_price

    edit_duty_in = st.time_input("Duty IN", pd.to_datetime(record_to_edit["duty_in"]).time(), key="edit_duty_in")
    edit_duty_out = st.time_input("Duty OUT", pd.to_datetime(record_to_edit["duty_out"]).time(), key="edit_duty_out")

    edit_in_time = datetime.combine(edit_date, edit_duty_in)
    edit_out_time = datetime.combine(edit_date, edit_duty_out)
    edit_hours = max((edit_out_time - edit_in_time).total_seconds()/3600, 0)

    if st.button("Save Changes to Record"):
        cursor.execute("""
        UPDATE sales SET 
            date=?, staff=?, fuel=?, nozzle=?, opening=?, closing=?,
            litres=?, price=?, total=?, duty_in=?, duty_out=?, hours=?
        WHERE rowid=?
        """, (
            str(edit_date), edit_staff, edit_fuel, edit_nozzle, edit_opening, edit_closing,
            edit_litres, edit_price, edit_total, str(edit_duty_in), str(edit_duty_out), edit_hours,
            edit_record_id
        ))
        conn.commit()
        st.success("Record Updated Successfully")
        st.experimental_rerun()
