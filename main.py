import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Choisons Petrol Pump",
    page_icon="⛽",
    layout="wide"
)

# Title
st.title("⛽ CHOISONS PETROL PUMP")
st.subheader("HPCL Dealer | Quality Fuel & Trusted Service")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Fuel Prices", "Daily Sales Entry", "Cash Balance", "Services", "Contact"]
)

# HOME PAGE
if menu == "Home":

    st.header("Welcome to Choisons Petrol Pump")

    # Add your image file here
    st.image("choisons_pump.png", use_container_width=True)

    st.markdown("""
    ### Our Fuel Station

    We provide:
    - High Quality HP Petrol
    - Diesel Fuel
    - Lubricants
    - Free Air & Water
    - Fast Billing
    - Friendly Staff
    """)

    st.success("Open 24 Hours 🚗")

# FUEL PRICE PAGE
elif menu == "Fuel Prices":

    st.header("Today's Fuel Prices")

    petrol = st.number_input("Petrol Price (₹)", value=105.00)
    diesel = st.number_input("Diesel Price (₹)", value=95.00)

    st.write("### Current Rates")
    st.write(f"Petrol : ₹ {petrol}")
    st.write(f"Diesel : ₹ {diesel}")

# SALES ENTRY PAGE
elif menu == "Daily Sales Entry":

    st.header("Daily Sales Entry")

    petrol_sales = st.number_input("Petrol Sales ₹", value=0)
    diesel_sales = st.number_input("Diesel Sales ₹", value=0)
    oil_sales = st.number_input("Oil Sales ₹", value=0)

    total_sales = petrol_sales + diesel_sales + oil_sales

    st.success(f"Total Sales ₹ {total_sales}")

# CASH BALANCE PAGE
elif menu == "Cash Balance":

    st.header("Cash Counter Balance")

    opening_cash = st.number_input("Opening Cash ₹", value=0)
    sales_cash = st.number_input("Cash Sales ₹", value=0)
    expenses = st.number_input("Expenses ₹", value=0)

    balance = opening_cash + sales_cash - expenses

    st.success(f"Closing Cash Balance ₹ {balance}")

# SERVICES PAGE
elif menu == "Services":

    st.header("Our Services")

    st.markdown("""
    - Petrol & Diesel
    - Engine Oil
    - Free Air
    - Drinking Water
    - UPI / Cash / Card Payment
    - Clean Restroom
    """)

# CONTACT PAGE
elif menu == "Contact":

    st.header("Contact Us")

    st.write("📍 Choisons Petrol Pump")
    st.write("Kannur Road, Calicut")
    st.write("📞 Phone: +91 8590304889")
    st.write("📧 Email: choisons@gmail.com")

    # Map location
    map_data = pd.DataFrame({
        'lat':[11.2588],
        'lon':[75.7804]
    })

    st.map(map_data)
