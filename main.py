import streamlit as st

# Page Config
st.set_page_config(
    page_title="Bharath Industrial | Welding Works",
    layout="wide"
)

# Header
st.title("🔧 Bharath Industrial Welding Works")
st.markdown("📞 **Contact:** 7902984770")

# Sidebar Navigation
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Price List", "Hen Cage Welding", "Welder Vacancy", "Contact"]
)

# ---------------- HOME ----------------
if menu == "Home":

    st.header("Bharath Industrial Welding Works")

    st.write(
        "Professional industrial welding, contract works, sheet installation "
        "and site welding services."
    )

    st.image(
        "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc",
        use_column_width=True
    )

    # Comment system
    st.subheader("Comments")

    if "comments" not in st.session_state:
        st.session_state.comments = []

    comment = st.text_input("Write a comment")

    if st.button("Post Comment"):
        if comment:
            st.session_state.comments.append(comment)

    for c in st.session_state.comments:
        st.write("💬", c)


# ---------------- PRICE LIST ----------------
elif menu == "Price List":

    st.header("Industrial Work Price List")

    data = {
        "Work Type": [
            "Contract Welding Work",
            "Sheet Installation",
            "Industrial Fabrication",
            "Site Welding Works",
            "Station Welding Works"
        ],
        "Price": [
            "₹1500 / Day",
            "₹120 / sq.ft",
            "₹2000 / Project",
            "₹1800 / Day",
            "₹1600 / Day"
        ]
    }

    st.table(data)


# ---------------- HEN CAGE ----------------
elif menu == "Hen Cage Welding":

    st.header("Hen Cage Welding Works")

    st.write(
        "We manufacture strong and durable poultry cages for farms "
        "and commercial poultry businesses."
    )

    st.image(
        "https://images.unsplash.com/photo-1598514982849-6e23b8c2a52b",
        use_column_width=True
    )

    st.markdown("""
    - Heavy duty iron cages  
    - Long life welding  
    - Custom sizes available  
    - Farm installation support
    """)


# ---------------- JOB VACANCY ----------------
elif menu == "Welder Vacancy":

    st.header("Welder Job Vacancy")

    st.info("""
    **Position:** Industrial Welder  

    **Experience:** 1-3 Years  

    **Location:** Site / Workshop  

    **Salary:** Negotiable
    """)

    st.success("📞 Interested candidates contact: 7902984770")


# ---------------- CONTACT ----------------
elif menu == "Contact":

    st.header("Contact Bharath Industrial")

    st.write(
        "For welding works, industrial fabrication and poultry cage welding."
    )

    st.write("📞 Phone: 7902984770")

    st.map()
