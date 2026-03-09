import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(
    page_title="Choisons Petrolium Private Limited",
    page_icon="⛽",
    layout="wide"
)

# ORANGE THEME
st.markdown("""
<style>

.stApp{
background-color:#fff7ef;
}

h1,h2,h3{
color:#ff6b00;
}

.stButton>button{
background-color:#ff6b00;
color:white;
border-radius:8px;
}

</style>
""", unsafe_allow_html=True)


# LOGIN SESSION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "attendance" not in st.session_state:
    st.session_state.attendance = []

if "sales" not in st.session_state:
    st.session_state.sales = []


# LOGIN PAGE
if not st.session_state.logged_in:

    st.title("⛽ Choisons Petrolium Private Limited")
    st.subheader("Staff Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid login")

else:

    st.sidebar.success("Logged in")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.selectbox(
        "Dashboard",
        ["Home","Staff Attendance","Nozzle Sales Entry","Fuel Prices","Services","Contact"]
    )

# HOME
    if menu == "Home":

        st.title("⛽ CHOISONS PETROLIUM PRIVATE LIMITED")
        st.success("24 Hour Fuel Service")

        image_path = "choisons_pump.png"

        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)

# STAFF ATTENDANCE
    elif menu == "Staff Attendance":

        st.header("Staff Attendance Register")

        col1,col2,col3 = st.columns(3)

        with col1:
            staff_name = st.text_input("Staff Name")

        with col2:
            staff_id = st.text_input("Staff ID")

        with col3:
            shift = st.selectbox("Shift",["Morning","Evening","Night"])

        if st.button("Mark Attendance"):

            st.session_state.attendance.append({
                "Date":date.today(),
                "Name":staff_name,
                "Staff ID":staff_id,
                "Shift":shift
            })

            st.success("Attendance recorded")

        if st.session_state.attendance:

            df = pd.DataFrame(st.session_state.attendance)

            st.subheader("Attendance List")
            st.dataframe(df,use_container_width=True)

# NOZZLE SALES ENTRY
    elif menu == "Nozzle Sales Entry":

        st.header("Nozzle Sales Entry")

        col1,col2,col3 = st.columns(3)

        with col1:
            nozzle = st.selectbox(
                "Nozzle",
                ["Petrol Nozzle 1","Petrol Nozzle 2","Diesel Nozzle 1","Diesel Nozzle 2"]
            )

        with col2:
            opening = st.number_input("Opening Meter",0)

        with col3:
            closing = st.number_input("Closing Meter",0)

        total_litres = closing - opening

        st.info(f"Total Litres Sold: {total_litres}")

        if st.button("Save Sales"):

            st.session_state.sales.append({
                "Date":date.today(),
                "Nozzle":nozzle,
                "Opening":opening,
                "Closing":closing,
                "Litres Sold":total_litres
            })

            st.success("Sales entry saved")

        if st.session_state.sales:

            df = pd.DataFrame(st.session_state.sales)

            st.subheader("Nozzle Sales Report")
            st.dataframe(df,use_container_width=True)

# FUEL PRICES
    elif menu == "Fuel Prices":

        st.header("Fuel Price Panel")

        col1,col2 = st.columns(2)

        with col1:
            petrol = st.number_input("Petrol Price ₹",105.00)

        with col2:
            diesel = st.number_input("Diesel Price ₹",95.00)

        st.success(f"Petrol ₹ {petrol}")
        st.success(f"Diesel ₹ {diesel}")

# SERVICES
    elif menu == "Services":

        st.header("Services")

        col1,col2 = st.columns(2)

        with col1:
            st.write("• Petrol & Diesel")
            st.write("• Engine Oil")
            st.write("• Free Air")
            st.write("• Drinking Water")

        with col2:
            st.write("• UPI / Cash / Card")
            st.write("• Clean Restroom")
            st.write("• Credit Sales Available")
            st.write("• 24x7 Service")

# CONTACT
    elif menu == "Contact":

        st.header("Contact")

        st.write("📍 Kannur Road, Calicut")
        st.write("📞 +91 8590304889")
        st.write("📧 choisons@gmail.com")

        map_data = pd.DataFrame({
            "lat":[11.2588],
            "lon":[75.7804]
        })

        st.map(map_data)
