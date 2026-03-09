import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Choisons Petrolium Private Limited",
    page_icon="⛽",
    layout="wide"
)

# ORANGE THEME STYLE
st.markdown("""
<style>

.stApp {
    background-color: #fff8f0;
}

h1, h2, h3 {
    color: #ff6b00;
}

div.stButton > button {
    background-color: #ff6b00;
    color: white;
    border-radius: 8px;
}

.sidebar .sidebar-content {
    background-color: #fff1e6;
}

</style>
""", unsafe_allow_html=True)

st.title("⛽ CHOISONS PETROLIUM PRIVATE LIMITED")
st.subheader("HPCL Dealer | Quality Fuel & Trusted Service")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Fuel Prices", "Daily Sales Entry", "Cash Balance", "Services", "Contact"]
)

# HOME PAGE
if menu == "Home":

    st.header("Welcome to Choisons Petrolium Private Limited")

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


# FUEL PRICES
elif menu == "Fuel Prices":

    st.header("Today's Fuel Prices")

    col1, col2 = st.columns(2)

    with col1:
        petrol = st.number_input("Petrol Price (₹)", value=105.00)

    with col2:
        diesel = st.number_input("Diesel Price (₹)", value=95.00)

    st.write(f"Petrol : ₹ {petrol}")
    st.write(f"Diesel : ₹ {diesel}")


# DAILY SALES
elif menu == "Daily Sales Entry":

    st.header("Daily Sales Entry")

    col1, col2, col3 = st.columns(3)

    with col1:
        petrol_sales = st.number_input("Petrol Sales ₹", 0)

    with col2:
        diesel_sales = st.number_input("Diesel Sales ₹", 0)

    with col3:
        oil_sales = st.number_input("Oil Sales ₹", 0)

    total = petrol_sales + diesel_sales + oil_sales

    st.success(f"Total Sales ₹ {total}")


# CASH BALANCE
elif menu == "Cash Balance":

    st.header("Cash Counter Balance")

    col1, col2, col3 = st.columns(3)

    with col1:
        opening = st.number_input("Opening Cash ₹", 0)

    with col2:
        sales = st.number_input("Cash Sales ₹", 0)

    with col3:
        expense = st.number_input("Expenses ₹", 0)

    balance = opening + sales - expense

    st.success(f"Closing Balance ₹ {balance}")


# SERVICES
elif menu == "Services":

    st.header("Our Services")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
- Petrol & Diesel  
- Engine Oil  
- Free Air  
- Drinking Water  
""")

    with col2:
        st.markdown("""
- UPI / Cash / Card Payment  
- Clean Restroom  
- **Credit Sales Available**  
- 24x7 Service  
""")


# CONTACT
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
