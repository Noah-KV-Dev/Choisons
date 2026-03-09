import streamlit as st

# Page config
st.set_page_config(page_title="HPCL Choices", layout="centered")

# Title
st.title("Hindustan Petroleum Choices Application")

# Image
st.image("https://images.unsplash.com/photo-rrUuQb4_7f4", use_column_width=True)

# Navigation
menu = st.sidebar.selectbox(
    "Menu",
    ["Home", "Apply", "Contact"]
)

# Home Page
if menu == "Home":
    st.header("Welcome")
    st.write("Welcome to the HPCL Choices application portal.")

# Apply Page
elif menu == "Apply":
    st.header("Application Form")

    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    address = st.text_area("Address")

    if st.button("Submit Application"):
        st.success("Application submitted successfully!")

# Contact Page
elif menu == "Contact":
    st.header("Contact Us")

    cname = st.text_input("Your Name")
    cemail = st.text_input("Your Email")
    message = st.text_area("Message")

    if st.button("Send Message"):
        st.success("Message sent successfully!")
