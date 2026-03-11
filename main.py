import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

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

# ---------------- DEFAULT FUEL PRICES ----------------

cursor.execute("SELECT COUNT(*) FROM fuel_price")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO fuel_price VALUES('Petrol',100)")
    cursor.execute("INSERT INTO fuel_price VALUES('Diesel',90)")
    cursor.execute("INSERT INTO fuel_price VALUES('Power Petrol',105)")
    conn.commit()

# ---------------- PAGE ----------------

st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

st.title("⛽ Choisons Petrol Pump Management System")

# ---------------- LOAD DATA ----------------

df = pd.read_sql("SELECT rowid,* FROM sales", conn)
staff_df = pd.read_sql("SELECT * FROM staff", conn)
price_df = pd.read_sql("SELECT * FROM fuel_price", conn)

price_dict = dict(zip(price_df["fuel"], price_df["price"]))

# ---------------- DUTY ----------------

st.subheader("Staff Duty Time")

col1,col2 = st.columns(2)

with col1:
    duty_in = st.time_input("Duty IN")

with col2:
    duty_out = st.time_input("Duty OUT")

in_time = datetime.combine(date.today(), duty_in)
out_time = datetime.combine(date.today(), duty_out)

hours = (out_time - in_time).total_seconds()/3600
if hours < 0:
    hours = 0

st.info(f"Work Hours: {round(hours,2)} hrs")

# ---------------- SALES ENTRY ----------------

st.subheader("Sales Entry")

col3,col4,col5 = st.columns(3)

staff_list = staff_df["name"].tolist()

with col3:
    staff = st.selectbox("Staff Name", staff_list)

with col4:
    entry_date = st.date_input("Date", date.today())

with col5:
    fuel = st.selectbox("Fuel Type",["Petrol","Diesel","Power Petrol"])

nozzle = st.selectbox("Nozzle",[
"Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4","Nozzle 5",
"Nozzle 6","Nozzle 7","Nozzle 8","Nozzle 9","Nozzle 10"
])

# ---------------- AUTO OPENING METRE ----------------

last = pd.read_sql(
    "SELECT closing FROM sales WHERE nozzle=? ORDER BY rowid DESC LIMIT 1",
    conn,
    params=(nozzle,)
)

if len(last) > 0:
    default_opening = last.iloc[0]["closing"]
else:
    default_opening = 0.0

col6,col7 = st.columns(2)

with col6:
    opening = st.number_input("Opening Metre", value=float(default_opening))

with col7:
    closing = st.number_input("Closing Metre")

litres = closing - opening
if litres < 0:
    litres = 0

price = price_dict[fuel]
total = litres * price

st.success(f"Litres Sold: {round(litres,2)} L")
st.success(f"Total Sale: ₹ {round(total,2)}")

# ---------------- SAVE ----------------

if st.button("Save Entry"):

    cursor.execute("""
    INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """,(
        str(entry_date),
        staff,
        fuel,
        nozzle,
        opening,
        closing,
        litres,
        price,
        total,
        str(duty_in),
        str(duty_out),
        hours
    ))

    conn.commit()

    st.success("Data Saved")

    st.rerun()

# ---------------- SALES TABLE ----------------

st.subheader("Sales Records")

st.dataframe(df, use_container_width=True)

# ---------------- DAILY SUMMARY ----------------

st.subheader("Daily Sales Summary")

today = str(date.today())

today_data = df[df["date"] == today]

st.metric("Litres Today", round(today_data["litres"].sum(),2))
st.metric("Sales Today", round(today_data["total"].sum(),2))

# ---------------- STAFF REPORT ----------------

st.subheader("Staff Total Litres")

staff_litres = df.groupby("staff")["litres"].sum().reset_index()

st.dataframe(staff_litres)

# ---------------- NOZZLE REPORT ----------------

st.subheader("Nozzle Sales")

nozzle_sales = df.groupby("nozzle")["litres"].sum().reset_index()

st.dataframe(nozzle_sales)

# ---------------- ADMIN PANEL ----------------

st.sidebar.title("Admin Panel")

admin_user = "admin"
admin_pass = "admin123"

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):

    if username == admin_user and password == admin_pass:
        st.session_state.admin_logged = True
        st.sidebar.success("Admin Logged In")
    else:
        st.sidebar.error("Invalid Login")

# ---------------- ADMIN CONTROLS ----------------

if st.session_state.admin_logged:

    st.sidebar.success("Admin Mode Active")

    if st.sidebar.button("Logout"):
        st.session_state.admin_logged = False
        st.rerun()

    st.subheader("⚠ Admin Controls")

    # -------- ADD STAFF --------

    st.write("Add New Staff")

    new_staff = st.text_input("Staff Name")

    if st.button("Add Staff"):

        cursor.execute(
        "INSERT INTO staff VALUES(?)",
        (new_staff,)
        )

        conn.commit()

        st.success("Staff Added")

        st.rerun()

    # -------- CHANGE FUEL PRICE --------

    st.write("Change Fuel Price")

    fuel_change = st.selectbox(
    "Fuel",
    ["Petrol","Diesel","Power Petrol"]
    )

    new_price = st.number_input("New Price")

    if st.button("Update Price"):

        cursor.execute(
        "UPDATE fuel_price SET price=? WHERE fuel=?",
        (new_price,fuel_change)
        )

        conn.commit()

        st.success("Price Updated")

        st.rerun()

    # -------- DELETE RECORD --------

    record_id = st.selectbox(
    "Select Record ID",
    df["rowid"]
    )

    if st.button("Delete Record"):

        cursor.execute(
        "DELETE FROM sales WHERE rowid=?",
        (record_id,)
        )

        conn.commit()

        st.warning("Record Deleted")

        st.rerun()

    # -------- DELETE ALL --------

    if st.button("Delete All Data"):

        cursor.execute("DELETE FROM sales")

        conn.commit()

        st.error("All Data Deleted")

        st.rerun()
