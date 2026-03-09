import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Choisons Petrol Pump",
    page_icon="⛽",
    layout="wide"
)

# Header
st.title("⛽ CHOISONS PETROL PUMP")
st.subheader("HPCL Dealer | Quality Fuel & Trusted Service")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Fuel Prices", "Daily Sales Entry", "Cash Balance", "Services", "Contact"]
)

# HOME PAGE
if menu == "Home":

    st.image("https://images.unsplash.com/photos/rrUuQb4_7f4", use_column_width=True)

    st.markdown("""
    ### Welcome to Choisons Petrol Pump

    We provide:
    - High Quality HP Petrol
    - Diesel Fuel
    - Lubricants
    - Air & Water Service
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

    petrol_sales = st.number_input("Petrol Sales ₹")
    diesel_sales = st.number_input("Diesel Sales ₹")
    oil_sales = st.number_input("Oil Sales ₹")

    total_sales = petrol_sales + diesel_sales + oil_sales

    st.write("### Total Sales")
    st.success(f"₹ {total_sales}")

# CASH BALANCE PAGE
elif menu == "Cash Balance":

    st.header("Cash Counter Balance")

    opening_cash = st.number_input("Opening Cash ₹")
    sales_cash = st.number_input("Cash Sales ₹")
    expenses = st.number_input("Expenses ₹")

    balance = opening_cash + sales_cash - expenses

    st.write("### Closing Cash Balance")
    st.success(f"₹ {balance}")

# SERVICES PAGE
elif menu == "Services":

    st.header("Our Services")

    st.markdown("""
    - Petrol & Diesel
    - Engine Oil
    - Free Air
    - Drinking Water
    - Fast Payment (UPI / Cash / Card)
    - Clean Restroom
    """)

# CONTACT PAGE
elif menu == "Contact":

    st.header("Contact Us")

    st.write("📍 Choisons Petrol Pump")
    st.write("Kannur Road, Calicut")
    st.write("📞 Phone: +91 8590304889")
    st.write("📧 Email: choisonscalicut@gmail.com")

    st.map(pd.DataFrame({
        'lat':[11.2588],
        'lon':[75.7804]
    }))
