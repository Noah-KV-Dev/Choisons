import streamlit as st
import pandas as pd
from datetime import date

# PAGE SETTINGS
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# STYLE
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');

html, body, [class*="css"] {
font-family: 'Lexend', sans-serif;
color:black;
}

.stApp{
background-color:#ff6f00;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.title("⛽ Choisons Petrol Pump Sales System")

# SESSION STORAGE
if "sales_data" not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(columns=[
        "Date",
        "Staff",
        "Nozzle",
        "Litres",
        "Price",
        "Total"
    ])

# ENTRY SECTION
st.subheader("Sales Entry")

col1,col2,col3 = st.columns(3)

with col1:
    staff = st.text_input("Staff Name")

with col2:
    entry_date = st.date_input("Date",date.today())

with col3:
    nozzle = st.selectbox("Nozzle",
    [
    "Nozzle 1","Nozzle 2","Nozzle 3","Nozzle 4","Nozzle 5",
    "Nozzle 6","Nozzle 7","Nozzle 8","Nozzle 9","Nozzle 10"
    ])

col4,col5 = st.columns(2)

with col4:
    litres = st.number_input("Litres Sold",min_value=0.0)

with col5:
    price = st.number_input("Price Per Litre",min_value=0.0)

# TOTAL
total = litres * price
st.success(f"Total Amount ₹ {round(total,2)}")

# SAVE BUTTON
if st.button("Save Entry"):

    new_row = pd.DataFrame({
        "Date":[entry_date],
        "Staff":[staff],
        "Nozzle":[nozzle],
        "Litres":[litres],
        "Price":[price],
        "Total":[total]
    })

    st.session_state.sales_data = pd.concat(
        [st.session_state.sales_data,new_row],
        ignore_index=True
    )

    st.success("Saved Successfully")

# SALES TABLE
st.subheader("Sales Data Table")

st.dataframe(
    st.session_state.sales_data,
    use_container_width=True
)

# DAILY TOTAL
st.subheader("Daily Total")

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

# MONTHLY STAFF REPORT
st.subheader("Monthly Litre Sale Per Staff")

if not df.empty:

    monthly_staff = df.groupby("Staff")["Litres"].sum().reset_index()

    monthly_staff.columns = ["Staff Name","Total Litres Sold"]

    st.dataframe(monthly_staff,use_container_width=True)

else:
    st.info("No Data Yet")

# NOZZLE REPORT
st.subheader("Nozzle Wise Sales")

if not df.empty:

    nozzle_report = df.groupby("Nozzle")["Litres"].sum().reset_index()

    nozzle_report.columns = ["Nozzle","Total Litres Sold"]

    st.dataframe(nozzle_report,use_container_width=True)
