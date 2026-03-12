import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import socket

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Choisons Petrol Pump", layout="wide")

# -------- ENTER KEY AUTO SUBMIT SCRIPT --------
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === "Enter") {
        const btn = window.parent.document.querySelector('button[kind="primary"]');
        if(btn){
            btn.click();
        }
    }
});
</script>
""", unsafe_allow_html=True)

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
paytm REAL,
hp_pay REAL,
cash REAL,
advance_paid REAL,
balance_cash REAL,
duty_in TEXT,
duty_out TEXT,
hours REAL,
ip_address TEXT,
credit_sale REAL
)
""")

cursor.execute("CREATE TABLE IF NOT EXISTS staff(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS fuel_prices(fuel TEXT UNIQUE,price REAL)")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cash_closing(
date TEXT,
system_cash REAL,
closing_cash REAL,
shortage REAL,
ip_address TEXT
)
""")

conn.commit()

# ---------------- DEFAULT PRICES ----------------
default_prices = {"Petrol":100.0,"Diesel":90.0,"Power Petrol":105.0}

for fuel,price in default_prices.items():
    cursor.execute("INSERT OR IGNORE INTO fuel_prices(fuel,price) VALUES (?,?)",(fuel,price))

conn.commit()

# ---------------- FUNCTIONS ----------------
def load_data():
    df = pd.read_sql("SELECT rowid,* FROM sales", conn)

    if not df.empty:
        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")

    return df

def export_excel(data):
    return data.to_csv(index=False).encode("utf-8")

df = load_data()

fuel_prices_df = pd.read_sql("SELECT * FROM fuel_prices", conn)
fuel_price_dict = dict(zip(fuel_prices_df["fuel"],fuel_prices_df["price"]))

staff_list = pd.read_sql("SELECT name FROM staff", conn)["name"].tolist()

# ---------------- TITLE ----------------
st.title("⛽ Choisons Petrol Pump Management System")
st.info("Super Fast Cashier Mode Enabled")

# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox(
"Menu",
["Sales Entry","Reports"]
)

# ---------------- SALES ENTRY ----------------
if menu == "Sales Entry":

    st.subheader("Fuel Entry (Fast Mode)")

    col1,col2,col3 = st.columns(3)

    with col1:
        staff = st.selectbox("Staff", staff_list)

    with col2:
        entry_date = st.date_input("Date", date.today())

    with col3:
        fuel = st.selectbox("Fuel",["Petrol","Diesel","Power Petrol"])

    price = fuel_price_dict.get(fuel,100)

    # -------- AUTO NEXT NOZZLE --------
    if "nozzle_index" not in st.session_state:
        st.session_state.nozzle_index = 0

    nozzle_list = [f"Nozzle {i}" for i in range(1,11)]

    nozzle = st.selectbox(
        "Nozzle",
        nozzle_list,
        index=st.session_state.nozzle_index
    )

    col4,col5 = st.columns(2)

    with col4:
        opening = st.number_input("Opening Meter",0.0)

    with col5:
        closing = st.number_input("Closing Meter",0.0)

    # -------- AUTO CALCULATE LITRES --------
    litres = max(closing - opening,0)

    total = litres * price

    st.success(f"Litres: {litres} L  |  Amount ₹ {total}")

    # -------- PAYMENTS --------
    st.subheader("Payments")

    col1,col2,col3,col4,col5 = st.columns(5)

    with col1:
        paytm = st.number_input("Paytm",0.0)

    with col2:
        hp_pay = st.number_input("HP Pay",0.0)

    with col3:
        cash = st.number_input("Cash",0.0)

    with col4:
        advance = st.number_input("Advance",0.0)

    with col5:
        credit = st.number_input("Credit",0.0)

    balance_cash = max(total-(paytm+hp_pay+cash+advance+credit),0)

    st.info(f"Balance Cash ₹ {balance_cash}")

    duty_in = st.time_input("Duty IN")
    duty_out = st.time_input("Duty OUT")

    in_time = datetime.combine(date.today(),duty_in)
    out_time = datetime.combine(date.today(),duty_out)

    hours = max((out_time-in_time).total_seconds()/3600,0)

    ip = socket.gethostbyname(socket.gethostname())

    # -------- SAVE ENTRY --------
    if st.button("Save Entry", type="primary"):

        cursor.execute("""
        INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(str(entry_date),staff,fuel,nozzle,opening,closing,litres,price,total,
             paytm,hp_pay,cash,advance,balance_cash,
             str(duty_in),str(duty_out),hours,ip,credit))

        conn.commit()

        # -------- AUTO NEXT NOZZLE --------
        st.session_state.nozzle_index += 1
        if st.session_state.nozzle_index >= len(nozzle_list):
            st.session_state.nozzle_index = 0

        st.success("Saved ✔")

        st.rerun()

    # -------- CASH SHORTAGE --------
    st.subheader("Cash Closing")

    system_cash = paytm + hp_pay + cash

    closing_cash = st.number_input("Actual Cash")

    shortage = closing_cash - system_cash

    if st.button("Check Cash"):

        cursor.execute("""
        INSERT INTO cash_closing VALUES (?,?,?,?,?)
        """,(str(entry_date),system_cash,closing_cash,shortage,ip))

        conn.commit()

        if shortage == 0:
            st.success("Cash Perfect")

        elif shortage < 0:
            st.error(f"Shortage ₹ {shortage}")

        else:
            st.warning(f"Extra ₹ {shortage}")

# ---------------- REPORTS ----------------
elif menu == "Reports":

    st.subheader("Dashboard")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric("Total Litres", df["litres"].sum())

    with col2:
        st.metric("Total Sales ₹", df["total"].sum())

    with col3:
        st.metric("Total Hours", df["hours"].sum())

    st.subheader("Fuel Sales")
    st.bar_chart(df.groupby("fuel")["litres"].sum())

    st.subheader("Staff Performance")
    st.bar_chart(df.groupby("staff")["total"].sum())

    st.subheader("Nozzle Sales")
    st.bar_chart(df.groupby("nozzle")["litres"].sum())

    st.dataframe(df)

    csv = export_excel(df)

    st.download_button(
        "Download Excel",
        csv,
        "petrol_sales.csv",
        "text/csv"
    )
