import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import socket

# ---------------- DATABASE ----------------
conn = sqlite3.connect("petrol_sales.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    date TEXT,
    staff TEXT,
    fuel TEXT,
    nozzle TEXT,
    opening REAL,
    closing REAL,
    litres REAL,
    price REAL,
    total REAL,
    duty_in TEXT,
    duty_out TEXT,
    hours REAL,
    ip_address TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS fuel_prices(
    fuel TEXT UNIQUE,
    price REAL
)
""")
conn.commit()

# ---------------- INITIALIZE DEFAULT FUEL PRICES ----------------
default_prices = {"Petrol":100.0,"Diesel":90.0,"Power Petrol":105.0}
for fuel, price in default_prices.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_prices(fuel,price) VALUES (?,?)",(fuel,price))
conn.commit()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');
html,body,[class*="css"]{
font-family:'Lexend',sans-serif;
color:black;
}
.stApp{
background-color:#ff6f00;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE & CONTACT ----------------
st.title("⛽ Choisons Petrol Pump Management System")
st.info("""
**Contact Details**  

Phone: +91 8590304889  
Email: kvpnaseeh@gmail.com / choisonscalicut@gmail.com  

Created by Nazeeh
""")

# ---------------- FETCH CURRENT FUEL PRICES ----------------
fuel_prices_df = pd.read_sql("SELECT * FROM fuel_prices", conn)
fuel_price_dict = dict(zip(fuel_prices_df['fuel'], fuel_prices_df['price']))

# ---------------- SESSION STATE FOR RERUN ----------------
if "rerun_flag" not in st.session_state: st.session_state.rerun_flag=False
if "admin_logged" not in st.session_state: st.session_state.admin_logged=False

# ---------------- STAFF LIST ----------------
staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()
if not staff_list: staff_list = ["Add Staff in Admin Panel"]

# ---------------- SALES ENTRY ----------------
if not st.session_state.admin_logged:
    st.subheader("Sales Entry")
    col1, col2, col3 = st.columns(3)

    with col1: staff = st.selectbox("Staff Name", staff_list)
    with col2: entry_date = st.date_input("Date", date.today())
    with col3: fuel = st.selectbox(
        "Fuel Type",
        [f"{f} - ₹{fuel_price_dict.get(f,100.0)}" for f in ["Petrol","Diesel","Power Petrol"]]
    )
    # Extract fuel name
    fuel = fuel.split(" - ")[0]

    current_fuel_price = fuel_price_dict.get(fuel,100.0)

    nozzle = st.selectbox("Nozzle",["Nozzle "+str(i) for i in range(1,11)])

    col4, col5 = st.columns(2)
    with col4: opening = st.number_input("Opening Metre")
    with col5: closing = st.number_input("Closing Metre")

    litres = max(closing-opening,0)
    price = current_fuel_price
    total = litres*price
    st.success(f"Litres Sold: {litres} L | Total: ₹ {total}")

    # Duty
    duty_in = st.time_input("Duty IN")
    duty_out = st.time_input("Duty OUT")
    in_time = datetime.combine(date.today(), duty_in)
    out_time = datetime.combine(date.today(), duty_out)
    hours = max((out_time-in_time).total_seconds()/3600,0)

    ip_address = socket.gethostbyname(socket.gethostname())

    if st.button("Save Entry"):
        cursor.execute("""
        INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(str(entry_date), staff, fuel, nozzle, opening, closing, litres, price, total,
             str(duty_in), str(duty_out), hours, ip_address))
        conn.commit()
        st.success("Data Saved")
        st.session_state.rerun_flag=True

# ---------------- LOAD SALES DATA ----------------
df = pd.read_sql("SELECT rowid,* FROM sales", conn)

st.subheader("Sales Records")
st.dataframe(df,use_container_width=True)

# ---------------- DASHBOARD METRICS ----------------
st.subheader("Daily Summary")
today_data = df[df["date"]==str(date.today())]
st.metric("Litres Today", round(today_data["litres"].sum(),2))
st.metric("Sales Today", round(today_data["total"].sum(),2))

st.subheader("Staff Monthly Summary")
staff_litres = df.groupby("staff")["litres"].sum().reset_index()
st.dataframe(staff_litres)
staff_hours = df.groupby("staff")["hours"].sum().reset_index()
st.dataframe(staff_hours)

st.subheader("Nozzle Sales")
nozzle_sales = df.groupby("nozzle")["litres"].sum().reset_index()
st.dataframe(nozzle_sales)

# ---------------- ADMIN LOGIN ----------------
st.sidebar.title("Admin Panel")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password",type="password")

if st.sidebar.button("Login"):
    if username=="admin" and password=="admin123":
        st.session_state.admin_logged=True
        st.sidebar.success("Admin Logged In")
    else:
        st.sidebar.error("Invalid Login")

# ---------------- ADMIN CONTROLS ----------------
if st.session_state.admin_logged:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"admin_logged":False, "rerun_flag":True}))

    st.subheader("⚠ Admin Controls")

    # ---------------- STAFF MANAGEMENT ----------------
    st.subheader("Staff Management")
    new_staff = st.text_input("Add New Staff")
    if st.button("Add Staff"):
        if new_staff.strip()!="":
            try:
                cursor.execute("INSERT INTO staff(name) VALUES (?)",(new_staff.strip(),))
                conn.commit()
                st.success(f"Staff '{new_staff}' added")
                st.session_state.rerun_flag=True
            except sqlite3.IntegrityError:
                st.error("Staff already exists")
    staff_df = pd.read_sql("SELECT * FROM staff",conn)
    st.dataframe(staff_df)

    # ---------------- FUEL PRICES ----------------
    st.subheader("Fuel Prices Management")
    for f in ["Petrol","Diesel","Power Petrol"]:
        new_p = st.number_input(f"Price for {f}", value=fuel_price_dict.get(f,100.0))
        if st.button(f"Update {f} Price"):
            cursor.execute("UPDATE fuel_prices SET price=? WHERE fuel=?",(new_p,f))
            conn.commit()
            fuel_price_dict[f]=new_p
            st.success(f"{f} price updated. New sales entries will use this price.")
            st.session_state.rerun_flag=True

    # ---------------- SALES RECORDS MANAGEMENT ----------------
    st.subheader("Manage Sales Records")
    if not df.empty:
        del_id = st.selectbox("Select Record ID to Delete",df["rowid"])
        if st.button("Delete Record"):
            cursor.execute("DELETE FROM sales WHERE rowid=?",(del_id,))
            conn.commit()
            st.warning("Record deleted")
            st.session_state.rerun_flag=True
        if st.button("Delete All Sales"):
            cursor.execute("DELETE FROM sales")
            conn.commit()
            st.error("All sales deleted")
            st.session_state.rerun_flag=True
    else:
        st.info("No sales records yet.")

    # ---------------- EDIT RECORD ----------------
    st.subheader("Edit Existing Record")
    if not df.empty:
        edit_id = st.selectbox("Select Record ID",df["rowid"])
        rec = df[df["rowid"]==edit_id]
        if not rec.empty:
            rec = rec.iloc[0]
            col1, col2, col3 = st.columns(3)
            with col1: edit_staff = st.selectbox("Staff",staff_list,index=staff_list.index(rec["staff"]))
            with col2: edit_date = st.date_input("Date",pd.to_datetime(rec["date"]))
            with col3: edit_fuel = st.selectbox("Fuel", ["Petrol","Diesel","Power Petrol"],
                                               index=["Petrol","Diesel","Power Petrol"].index(rec["fuel"]))
            edit_nozzle = st.selectbox("Nozzle",["Nozzle "+str(i) for i in range(1,11)],
                                       index=int(rec["nozzle"].split()[1])-1)
            col4,col5 = st.columns(2)
            with col4: edit_opening = st.number_input("Opening Metre",rec["opening"])
            with col5: edit_closing = st.number_input("Closing Metre",rec["closing"])
            edit_litres = max(edit_closing-edit_opening,0)
            edit_price = fuel_price_dict.get(edit_fuel,100.0)
            edit_total = edit_litres*edit_price
            edit_duty_in = st.time_input("Duty IN",pd.to_datetime(rec["duty_in"]).time())
            edit_duty_out = st.time_input("Duty OUT",pd.to_datetime(rec["duty_out"]).time())
            edit_hours = max((datetime.combine(edit_date,edit_duty_out)-datetime.combine(edit_date,edit_duty_in)).total_seconds()/3600,0)
            if st.button("Save Changes"):
                cursor.execute("""
                UPDATE sales SET date=?, staff=?, fuel=?, nozzle=?, opening=?, closing=?,
                    litres=?, price=?, total=?, duty_in=?, duty_out=?, hours=?
                WHERE rowid=?
                """,(str(edit_date), edit_staff, edit_fuel, edit_nozzle, edit_opening, edit_closing,
                     edit_litres, edit_price, edit_total, str(edit_duty_in), str(edit_duty_out), edit_hours, edit_id))
                conn.commit()
                st.success("Record updated")
                st.session_state.rerun_flag=True

# ---------------- SAFE RERUN ----------------
if st.session_state.rerun_flag:
    st.session_state.rerun_flag=False
    st.experimental_rerun()
