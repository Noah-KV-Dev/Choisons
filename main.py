import streamlit as st
import pandas as pd
from datetime import date

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Choisons Petrol Pump",
    page_icon="⛽",
    layout="wide"
)

# ---------------- STYLE ----------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Lexend', sans-serif;
    color: black;
}

.stApp {
    background-color:#ff6f00;
}

h1,h2,h3{
color:black;
}

div[data-baseweb="select"] > div{
background-color:white;
color:black;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.title("⛽ Choisons Petrol Pump Management System")

# ---------------- PUMP IMAGE ----------------

st.image("choisons_pump.png", use_column_width=True)

st.divider()

# ---------------- SESSION STORAGE ----------------

if "sales_data" not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(columns=[
        "Date",
        "Staff Name",
        "Fuel Type",
        "Nozzle",
        "Litres",
        "Price per Litre",
        "Total Amount"
    ])

# ---------------- STAFF ENTRY ----------------

st.subheader("👨‍💼 Staff Sales Entry")

col1,col2,col3 = st.columns(3)

with col1:
    staff_name = st.text_input("Staff Name")

with col2:
    entry_date = st.date_input("Date", date.today())

with col3:
    fuel_type = st.selectbox(
        "Fuel Type",
        ["Petrol","Diesel","Power Petrol"]
    )

# ---------------- NOZZLE SALES ----------------

st.subheader("⛽ Nozzle Sales Entry")

col4,col5,col6 = st.columns(3)

with col4:
    nozzle = st.selectbox(
        "Select Nozzle",
        ["Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4"]
    )

with col5:
    litres = st.number_input(
        "Litres Sold",
        min_value=0.0,
        step=0.01
    )

with col6:
    price = st.number_input(
        "Price Per Litre",
        min_value=0.0,
        step=0.01
    )

# ---------------- TOTAL ----------------

total = litres * price

st.success(f"Total Amount: ₹ {round(total,2)}")

# ---------------- SAVE BUTTON ----------------

if st.button("Save Sales Entry"):

    new_row = pd.DataFrame({
        "Date":[entry_date],
        "Staff Name":[staff_name],
        "Fuel Type":[fuel_type],
        "Nozzle":[nozzle],
        "Litres":[litres],
        "Price per Litre":[price],
        "Total Amount":[total]
    })

    st.session_state.sales_data = pd.concat(
        [st.session_state.sales_data,new_row],
        ignore_index=True
    )

    st.success("Sales Entry Saved")

# ---------------- SALES RECORD ----------------

st.subheader("📊 Sales Records")

st.dataframe(
    st.session_state.sales_data,
    use_container_width=True
)

# ---------------- DAILY SUMMARY ----------------

st.subheader("📅 Daily Summary")

today = pd.to_datetime(date.today())

if not st.session_state.sales_data.empty:

    df = st.session_state.sales_data.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    today_sales = df[df["Date"] == today]

    daily_litres = today_sales["Litres"].sum()
    daily_amount = today_sales["Total Amount"].sum()

else:
    daily_litres = 0
    daily_amount = 0

col7,col8 = st.columns(2)

with col7:
    st.metric("Total Litres Sold Today", round(daily_litres,2))

with col8:
    st.metric("Total Sales Today", f"₹ {round(daily_amount,2)}")

# ---------------- MONTHLY REPORT ----------------

st.subheader("📈 Monthly Meter Report")

if not st.session_state.sales_data.empty:

    df = st.session_state.sales_data.copy()

    df["Date"] = pd.to_datetime(df["Date"])

    monthly = df.groupby(
        df["Date"].dt.to_period("M")
    )[["Litres","Total Amount"]].sum()

    st.dataframe(monthly)

else:
    st.info("No sales data available yet.")
