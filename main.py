import streamlit as st
import pandas as pd
from datetime import date

# PAGE CONFIG
st.set_page_config(
    page_title="Choisons Petrol Pump",
    page_icon="⛽",
    layout="wide"
)

# STYLE
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');

html, body, [class*="css"]{
font-family:'Lexend',sans-serif;
color:black;
}

.stApp{
background-color:#ff6f00;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.title("⛽ Choisons Petrol Pump Management System")

st.divider()

# SESSION STORAGE
if "sales_data" not in st.session_state:

    st.session_state.sales_data = pd.DataFrame(columns=[
        "Date",
        "Staff",
        "Fuel",
        "Nozzle",
        "Opening Metre",
        "Closing Metre",
        "Litres",
        "Price",
        "Total"
    ])

# ---------------- FUEL PRICE SETTINGS ----------------

st.subheader("Fuel Prices")

colp1,colp2,colp3 = st.columns(3)

with colp1:
    petrol_price = st.number_input("Petrol Price",value=100.0)

with colp2:
    diesel_price = st.number_input("Diesel Price",value=90.0)

with colp3:
    power_price = st.number_input("Power Petrol Price",value=105.0)

# ---------------- SALES ENTRY ----------------

st.subheader("Sales Entry")

col1,col2,col3 = st.columns(3)

with col1:
    staff = st.text_input("Staff Name")

with col2:
    entry_date = st.date_input("Date",date.today())

with col3:
    fuel = st.selectbox(
        "Fuel Type",
        ["Petrol","Diesel","Power Petrol"]
    )

# NOZZLE
nozzle = st.selectbox(
    "Nozzle",
[
"Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4","Nozzle 5",
"Nozzle 6","Nozzle 7","Nozzle 8","Nozzle 9","Nozzle 10"
]
)

# METRE READINGS
col4,col5 = st.columns(2)

with col4:
    opening = st.number_input("Opening Metre",min_value=0.0)

with col5:
    closing = st.number_input("Closing Metre",min_value=0.0)

# LITRE CALCULATION
litres = closing - opening

if litres < 0:
    litres = 0

# PRICE SELECT
if fuel == "Petrol":
    price = petrol_price
elif fuel == "Diesel":
    price = diesel_price
else:
    price = power_price

# TOTAL
total = litres * price

st.success(f"Litres Sold: {round(litres,2)} L")

st.success(f"Total Sale Amount: ₹ {round(total,2)}")

# SAVE DATA
if st.button("Save Entry"):

    new_row = pd.DataFrame({
        "Date":[entry_date],
        "Staff":[staff],
        "Fuel":[fuel],
        "Nozzle":[nozzle],
        "Opening Metre":[opening],
        "Closing Metre":[closing],
        "Litres":[litres],
        "Price":[price],
        "Total":[total]
    })

    st.session_state.sales_data = pd.concat(
        [st.session_state.sales_data,new_row],
        ignore_index=True
    )

    st.success("Entry Saved")

# ---------------- SALES TABLE ----------------

st.subheader("Sales Data")

st.dataframe(
    st.session_state.sales_data,
    use_container_width=True
)

# ---------------- DAILY SUMMARY ----------------

st.subheader("Daily Sales Summary")

df = st.session_state.sales_data

if not df.empty:

    df["Date"] = pd.to_datetime(df["Date"])

    today = pd.to_datetime(date.today())

    today_data = df[df["Date"] == today]

    daily_litre = today_data["Litres"].sum()
    daily_amount = today_data["Total"].sum()

else:
    daily_litre = 0
    daily_amount = 0

col6,col7 = st.columns(2)

with col6:
    st.metric("Total Litres Today",round(daily_litre,2))

with col7:
    st.metric("Total Sales Today",f"₹ {round(daily_amount,2)}")

# ---------------- MONTHLY STAFF REPORT ----------------

st.subheader("Monthly Litre Sale Per Staff")

if not df.empty:

    monthly_staff = df.groupby("Staff")["Litres"].sum().reset_index()

    st.dataframe(monthly_staff,use_container_width=True)

# ---------------- NOZZLE REPORT ----------------

st.subheader("Nozzle Sales Report")

if not df.empty:

    nozzle_sales = df.groupby("Nozzle")["Litres"].sum().reset_index()

    st.dataframe(nozzle_sales,use_container_width=True)
