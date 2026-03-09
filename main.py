import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(
    page_title="Choisons Petrolium Private Limited",
    page_icon="⛽",
    layout="wide"
)

# THEME + FONT
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Lexend', sans-serif;
    color: black;
}

/* MAIN BACKGROUND */
.stApp{
    background-color:#ff6b00;
}

/* TEXT */
h1,h2,h3,h4,h5,p,span,label{
    color:black;
}

/* BUTTON STYLE */
.stButton>button{
    background-color:white;
    color:black;
    border-radius:8px;
}

/* SIDEBAR */
section[data-testid="stSidebar"]{
    background-color:#ff8c42;
}

/* SELECT BOX CLEAR STYLE */
div[data-baseweb="select"]{
    background-color:white;
    border-radius:8px;
}

</style>
""", unsafe_allow_html=True)


# DATA STORAGE
if "attendance" not in st.session_state:
    st.session_state.attendance = []

if "sales" not in st.session_state:
    st.session_state.sales = []


# SIDEBAR MENU
menu = st.sidebar.selectbox(
    "Dashboard",
    ["Home","Staff Attendance","Nozzle Sales","Fuel Prices","Cash Balance","Services","Contact"]
)


# HOME
if menu=="Home":

    st.title("⛽ CHOISONS PETROLIUM PRIVATE LIMITED")
    st.success("24 Hour Fuel Service")

    image_path="choisons_pump.png"

    if os.path.exists(image_path):
        st.image(image_path,use_container_width=True)

    st.write("HPCL Dealer | Quality Fuel | Trusted Service")


# STAFF ATTENDANCE
elif menu=="Staff Attendance":

    st.header("Staff Attendance")

    col1,col2,col3 = st.columns(3)

    with col1:
        name = st.text_input("Staff Name")

    with col2:
        staff_id = st.text_input("Staff ID")

    with col3:
        shift = st.selectbox("Shift",["Morning","Evening","Night"])

    if st.button("Mark Attendance"):

        st.session_state.attendance.append({
            "Date":date.today(),
            "Name":name,
            "Staff ID":staff_id,
            "Shift":shift
        })

        st.success("Attendance saved")

    if st.session_state.attendance:

        df = pd.DataFrame(st.session_state.attendance)

        st.dataframe(df,use_container_width=True)


# NOZZLE SALES
elif menu=="Nozzle Sales":

    st.header("Nozzle Sales Entry")

    col1,col2,col3 = st.columns(3)

    with col1:
        nozzle = st.selectbox(
            "Nozzle",
            ["Petrol 1","Petrol 2","Power Petrol","Diesel 1","Diesel 2"]
        )

    with col2:
        opening = st.number_input("Opening Meter",0)

    with col3:
        closing = st.number_input("Closing Meter",0)

    litres = closing-opening

    st.info(f"Total Litres Sold: {litres}")

    if st.button("Save Sales"):

        st.session_state.sales.append({
            "Date":date.today(),
            "Nozzle":nozzle,
            "Opening":opening,
            "Closing":closing,
            "Litres":litres
        })

        st.success("Sales saved")

    if st.session_state.sales:

        df = pd.DataFrame(st.session_state.sales)

        st.dataframe(df,use_container_width=True)


# FUEL PRICES
elif menu=="Fuel Prices":

    st.header("Fuel Prices")

    col1,col2 = st.columns(2)

    with col1:
        petrol = st.number_input("Petrol Price ₹",105.00)

    with col2:
        diesel = st.number_input("Diesel Price ₹",95.00)

    st.success(f"Petrol ₹ {petrol}")
    st.success(f"Diesel ₹ {diesel}")


# CASH BALANCE
elif menu=="Cash Balance":

    st.header("Cash Counter")

    col1,col2,col3 = st.columns(3)

    with col1:
        opening = st.number_input("Opening Cash ₹",0)

    with col2:
        sales = st.number_input("Cash Sales ₹",0)

    with col3:
        expense = st.number_input("Expenses ₹",0)

    balance = opening+sales-expense

    st.success(f"Closing Balance ₹ {balance}")


# SERVICES
elif menu=="Services":

    st.header("Services")

    col1,col2 = st.columns(2)

    with col1:
        st.write("• Petrol & Diesel")
        st.write("• Power Petrol")
        st.write("• Engine Oil")
        st.write("• Free Air")

    with col2:
        st.write("• Drinking Water")
        st.write("• UPI / Cash / Card")
        st.write("• Credit Sales Available")
        st.write("• 24x7 Service")


# CONTACT
elif menu=="Contact":

    st.header("Contact")

    st.write("📍 Kannur Road, Calicut")
    st.write("📞 +91 8590304889")
    st.write("📧 choisons@gmail.com")

    map_data = pd.DataFrame({
        "lat":[11.2588],
        "lon":[75.7804]
    })

    st.map(map_data)
