import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

# DATABASE
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

conn.commit()

# PAGE CONFIG
st.set_page_config(page_title="Choisons Petrol Pump",layout="wide")

# STYLE
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
""",unsafe_allow_html=True)

st.title("⛽ Choisons Petrol Pump Management System")
# ---------------- MANAGER CONTACT ----------------

st.subheader(" Contact Details")

col1, col2 = st.columns(2)
with col1:
    manager_name = "Manager Name"
    phone = "+91 8590304889"
    email = "kvpnaseeh@gmail.com\n choisonscalicut@gmail.com"
   
st.info(f"""
Phone: {phone}
Email: {email}
""")                                         

# ---------------- FUEL PRICES ----------------

st.subheader("Fuel Prices")

col1,col2,col3 = st.columns(3)

with col1:
    petrol_price = st.number_input("Petrol Price",value=100.0)

with col2:
    diesel_price = st.number_input("Diesel Price",value=90.0)

with col3:
    power_price = st.number_input("Power Petrol Price",value=105.0)

# ---------------- STAFF DUTY ----------------

st.subheader("Staff Duty Time")

col4,col5 = st.columns(2)

with col4:
    duty_in = st.time_input("Duty IN")

with col5:
    duty_out = st.time_input("Duty OUT")

# CALCULATE HOURS
in_time = datetime.combine(date.today(), duty_in)
out_time = datetime.combine(date.today(), duty_out)

hours = (out_time - in_time).total_seconds() / 3600

if hours < 0:
    hours = 0

st.info(f"Work Hours: {round(hours,2)} hrs")

# ---------------- SALES ENTRY ----------------

st.subheader("Sales Entry")

col6,col7,col8 = st.columns(3)

with col6:
    staff = st.text_input("Staff Name")

with col7:
    entry_date = st.date_input("Date",date.today())

with col8:
    fuel = st.selectbox("Fuel Type",["Petrol","Diesel","Power Petrol"])

# NOZZLE
nozzle = st.selectbox("Nozzle",[
"Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4","Nozzle 5",
"Nozzle 6","Nozzle 7","Nozzle 8","Nozzle 9","Nozzle 10"
])

# METRE
col9,col10 = st.columns(2)

with col9:
    opening = st.number_input("Opening Metre")

with col10:
    closing = st.number_input("Closing Metre")

# LITRE CALCULATION
litres = closing - opening
if litres < 0:
    litres = 0

# PRICE
if fuel == "Petrol":
    price = petrol_price
elif fuel == "Diesel":
    price = diesel_price
else:
    price = power_price

# TOTAL
total = litres * price

st.success(f"Litres Sold: {round(litres,2)} L")
st.success(f"Total Sale: ₹ {round(total,2)}")

# SAVE
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

# ---------------- DATA TABLE ----------------

df = pd.read_sql("SELECT * FROM sales",conn)

st.subheader("Sales Records")

st.dataframe(df,use_container_width=True)

# ---------------- DAILY SALES ----------------

st.subheader("Daily Sales Summary")

today = str(date.today())

today_data = df[df["date"] == today]

st.metric("Litres Today",round(today_data["litres"].sum(),2))
st.metric("Sales Today",round(today_data["total"].sum(),2))

# ---------------- MONTHLY STAFF LITRES ----------------

st.subheader("Monthly Litre Sales Per Staff")

staff_litres = df.groupby("staff")["litres"].sum().reset_index()

st.dataframe(staff_litres)

# ---------------- MONTHLY STAFF HOURS ----------------

st.subheader("Monthly Staff Working Hours")

staff_hours = df.groupby("staff")["hours"].sum().reset_index()

st.dataframe(staff_hours)

# ---------------- NOZZLE SALES ----------------

st.subheader("Nozzle Sales")

nozzle_sales = df.groupby("nozzle")["litres"].sum().reset_index()

st.dataframe(nozzle_sales)
