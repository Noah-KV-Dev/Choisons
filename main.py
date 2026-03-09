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

html, body, [class*="css"]  {
    font-family: 'Lexend', sans-serif;
    color: black;
}

.stApp{
    background-color:#fff7ef;
}

h1,h2,h3,h4{
color:black;
}

.stButton>button{
background-color:#ff6b00;
color:white;
border-radius:8px;
}

</style>
""", unsafe_allow_html=True)


# SESSION STATES
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "staff_accounts" not in st.session_state:
    st.session_state.staff_accounts = {"admin":"1234"}

if "attendance" not in st.session_state:
    st.session_state.attendance = []

if "sales" not in st.session_state:
    st.session_state.sales = []


# AUTH MENU
auth_menu = st.sidebar.selectbox(
    "Account",
    ["Login","Signup"]
)

# LOGIN
if auth_menu == "Login" and not st.session_state.logged_in:

    st.title("⛽ Choisons Petrolium Private Limited")
    st.subheader("Staff Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        if username in st.session_state.staff_accounts and \
           st.session_state.staff_accounts[username]==password:

            st.session_state.logged_in = True
            st.session_state.user = username

            st.success(f"Welcome {username}")
            st.rerun()

        else:
            st.error("Invalid login")

# SIGNUP
elif auth_menu == "Signup" and not st.session_state.logged_in:

    st.title("Staff Signup")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password",type="password")

    if st.button("Create Account"):

        if new_user in st.session_state.staff_accounts:

            st.warning("Username already exists")

        else:

            st.session_state.staff_accounts[new_user] = new_pass

            st.success("Account created successfully")


# DASHBOARD AFTER LOGIN
if st.session_state.logged_in:

    st.sidebar.success(f"Logged in as {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()

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
                ["Petrol 1","Petrol 2","Diesel 1","Diesel 2"]
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
            st.write("• Engine Oil")
            st.write("• Free Air")
            st.write("• Drinking Water")

        with col2:
            st.write("• UPI / Cash / Card")
            st.write("• Clean Restroom")
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
