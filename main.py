# ---------------- ADMIN SIDEBAR ----------------
st.sidebar.title("Admin Panel")

# Initialize session state
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if not st.session_state.admin_logged:
    # Show login form
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.admin_logged = True
            st.sidebar.success("Admin Logged In")
        else:
            st.sidebar.error("Invalid Credentials")
else:
    # Admin options
    st.sidebar.success("Admin Mode")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.admin_logged = False
        st.experimental_rerun()  # refresh page to show login again

    # Staff management
    st.sidebar.subheader("Add Staff")
    new_staff = st.sidebar.text_input("Staff Name", key="staff_add")
    if st.sidebar.button("Add Staff", key="add_staff_btn"):
        try:
            cursor.execute("INSERT INTO staff(name) VALUES (?)", (new_staff,))
            conn.commit()
            st.sidebar.success(f"Staff '{new_staff}' added")
            st.experimental_rerun()
        except sqlite3.IntegrityError:
            st.sidebar.error("Staff already exists")

    # Creditor management
    st.sidebar.subheader("Add Creditor")
    new_creditor = st.sidebar.text_input("Creditor Name", key="creditor_add")
    if st.sidebar.button("Add Creditor", key="add_creditor_btn"):
        try:
            cursor.execute("INSERT INTO creditors(name) VALUES (?)", (new_creditor,))
            conn.commit()
            st.sidebar.success(f"Creditor '{new_creditor}' added")
            st.experimental_rerun()
        except sqlite3.IntegrityError:
            st.sidebar.error("Creditor already exists")

    # Fuel price management
    st.sidebar.subheader("Fuel Price Update")
    for fuel in ["Petrol", "Diesel", "Power Petrol"]:
        new_price = st.sidebar.number_input(f"{fuel} Price", value=fuel_price_dict.get(fuel, 100.0), key=f"{fuel}_price")
        if st.sidebar.button(f"Update {fuel} Price", key=f"update_{fuel}"):
            cursor.execute("UPDATE fuel_prices SET price=? WHERE fuel=?", (new_price, fuel))
            conn.commit()
            st.sidebar.success(f"{fuel} price updated")
            st.experimental_rerun()
