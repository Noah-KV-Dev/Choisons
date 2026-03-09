import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Choisons Petrol Pump",
    page_icon="⛽",
    layout="wide"
)

st.title("⛽ CHOISONS PETROL PUMP")
st.subheader("HPCL Dealer | Quality Fuel & Trusted Service")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Fuel Prices", "Daily Sales Entry", "Cash Balance", "Services", "Contact"]
)

# HOME PAGE
if menu == "Home":

    st.header("Welcome to Choisons Petrol Pump")

    image_path = "choisons_pump.png"

    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning("Petrol pump image not found. Please upload 'choisons_pump.png'.")

    st.markdown("""
    ### Our Fuel Station

    - High Quality HP Petrol
    - Diesel Fuel
    - Lubricants
    - Free Air & Water
    - Fast Billing
    - Friendly Staff
    """)

    st.success("Open 24 Hours 🚗")


elif menu == "Fuel Prices":

    st.header("Today's Fuel Prices")

    petrol = st.number_input("Petrol Price (₹)", value=105.00)
    diesel = st.number_input("Diesel Price (₹)", value=95.00)

    st.write(f"Petrol : ₹ {petrol}")
    st.write(f"Diesel : ₹ {diesel}")


elif menu == "Daily Sales Entry":

    st.header("Daily Sales Entry")

    petrol_sales = st.number_input("Petrol Sales ₹", 0)
    diesel_sales = st.number_input("Diesel Sales ₹", 0)
    oil_sales = st.number_input("Oil Sales ₹", 0)

    total = petrol_sales + diesel_sales + oil_sales

    st.success(f"Total Sales ₹ {total}")


elif menu == "Cash Balance":

    st.header("Cash Counter Balance")

    opening = st.number_input("Opening Cash ₹", 0)
    sales = st.number_input("Cash Sales ₹", 0)
    expense = st.number_input("Expenses ₹", 0)

    balance = opening + sales - expense

    st.success(f"Closing Balance ₹ {balance}")


elif menu == "Services":

    st.header("Our Services")

    st.markdown("""
    - Petrol & Diesel
    - Engine Oil
    - Free Air
    - Drinking Water
    - UPI / Cash / Card
    - Clean Restroom
    """)


elif menu == "Contact":

    st.header("Contact Us")

    st.write("📍 Choisons Petrol Pump")
    st.write("Kannur Road, Calicut")
    st.write("📞 Phone: +91 8590304889")
    st.write("📧 Email: choisons@gmail.com")

    map_data = pd.DataFrame({
        "lat":[11.2588],
        "lon":[75.7804]
    })

    st.map(map_data)
