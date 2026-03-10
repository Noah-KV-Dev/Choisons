import streamlit as st

st.set_page_config(page_title="Bharath Industrial", layout="wide")

# CSS must be inside a string
st.markdown("""
<style>

.header{
background:#1877f2;
color:white;
padding:15px;
font-size:24px;
font-weight:bold;
}

.card{
background:white;
padding:20px;
border-radius:10px;
box-shadow:0 0 5px rgba(0,0,0,0.1);
margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header">Bharath Industrial | 📞 7902984770</div>', unsafe_allow_html=True)

# Sidebar menu
menu = st.sidebar.selectbox(
"Navigation",
["Home","Price List","Hen Cage Welding","Welder Vacancy","Contact"]
)

# Home Page
if menu == "Home":
    st.header("Bharath Industrial Welding Works")
    st.write("Professional industrial welding, fabrication and site works.")

# Price List
elif menu == "Price List":
    st.header("Industrial Work Price List")
    st.table({
        "Work Type":[
            "Contract Welding Work",
            "Sheet Installation",
            "Industrial Fabrication",
            "Site Welding Works",
            "Station Welding Works"
        ],
        "Price":[
            "₹1500 / Day",
            "₹120 / sq.ft",
            "₹2000 / Project",
            "₹1800 / Day",
            "₹1600 / Day"
        ]
    })

# Hen Cage
elif menu == "Hen Cage Welding":
    st.header("Hen Cage Welding Works")
    st.write("Strong poultry cages with heavy duty welding.")

# Job
elif menu == "Welder Vacancy":
    st.header("Welder Job Vacancy")
    st.write("Experience: 1-3 Years")
    st.write("Salary: Negotiable")
    st.write("📞 Contact: 7902984770")

# Contact
elif menu == "Contact":
    st.header("Contact Bharath Industrial")
    st.write("📞 7902984770")
