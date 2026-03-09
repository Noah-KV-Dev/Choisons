import streamlit as st

st.set_page_config(page_title="HPCL Choices", layout="centered")

st.title("Hindustan Petroleum Choices Application")

# Working Unsplash direct image
st.image(
    "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd",
    use_container_width=True
)

menu = st.sidebar.selectbox(
    "Menu",
    ["Home", "Apply", "Contact"]
)

if menu == "Home":
    st.header("Welcome")
    st.write("Welcome to the HPCL Choices application portal.")

elif menu == "Apply":
    st.header("Application Form")

    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    address = st.text_area("Address")

    if st.button("Submit Application"):
        st.success("Application submitted successfully!")

elif menu == "Contact":
    st.header("Contact Us")

    cname = st.text_input("Your Name")
    cemail = st.text_input("Your Email")
    message = st.text_area("Message")

    if st.button("Send Message"):
        st.success("Message sent successfully!")
