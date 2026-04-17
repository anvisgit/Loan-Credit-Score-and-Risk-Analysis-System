import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.db_connect import get_kpis, get_monthly_repayments, fetch_df

st.set_page_config(page_title="LoanIQ", page_icon=None, layout="wide", initial_sidebar_state="expanded")



with st.sidebar:
    st.markdown("### LoanIQ")
    st.markdown("---")
    st.markdown("**Navigation**")
    st.markdown("""
- Home (current)
- Customer Management
- Loan Application
- EMI Tracker
- Administration
""")
    st.markdown("---")
    st.caption("PostgreSQL + scikit-learn + Streamlit")

st.markdown("# Loan Management System")
st.caption("Portfolio overview — real-time data from PostgreSQL")

try:
    kpis = get_kpis()
except ValueError as e:
    st.error(f"Database Configuration Missing: {e}")
    st.info("Please provide your PostgreSQL credentials below to connect.")
    from dotenv import set_key
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    with st.form("db_config_form"):
        host = st.text_input("Host", value=os.getenv("DB_HOST", "localhost"))
        port = st.text_input("Port", value=os.getenv("DB_PORT", "5432"))
        dbname = st.text_input("Database Name", value=os.getenv("DB_NAME", "loandb"))
        user = st.text_input("User Name", value=os.getenv("DB_USER", "postgres"))
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Save Credentials & Connect", use_container_width=True):
            set_key(env_path, "DB_HOST", host.strip() or "localhost")
            set_key(env_path, "DB_PORT", port.strip() or "5432")
            set_key(env_path, "DB_NAME", dbname.strip() or "loandb")
            set_key(env_path, "DB_USER", user.strip() or "postgres")
            set_key(env_path, "DB_PASSWORD", pwd.strip())
            st.rerun()
    st.stop()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.info("Ensure PostgreSQL is running and the credentials in .env are correct.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Customers", kpis["total_customers"])
with c2:
    st.metric("Active Loans", kpis["active_loans"])
with c3:
    st.metric("Defaulters", kpis["defaulters"])
with c4:
    st.metric("Penalties Collected", f"Rs.{kpis['penalties_collected']:,.0f}")

try:
    rep = get_monthly_repayments()
    if not rep.empty:
        # Prettify the dataframe before showing
        rep = rep.rename(columns={"month": "Month", "total_collected": "Total Collected (Rs.)", "payment_count": "Payments Made"})
        st.dataframe(rep, use_container_width=True, hide_index=True)
    else:
        st.info("No repayment data yet.")
except Exception as e:
    st.error(str(e))

st.subheader("Recent Loan Activity")
try:
    df = fetch_df("""
        SELECT l.loan_id, c.name AS customer, lt.type_name AS type,
               l.loan_amount, l.interest_rate, l.tenure, l.current_status, l.disbursed_date
        FROM loan l
        JOIN customer c   ON c.customer_id   = l.customer_id
        JOIN loan_type lt ON lt.loan_type_id = l.loan_type_id
        ORDER BY l.loan_id DESC LIMIT 10
    """)
    df["loan_amount"]    = df["loan_amount"].apply(lambda x: f"Rs.{float(x):,.2f}")
    df["interest_rate"]  = df["interest_rate"].apply(lambda x: f"{float(x):.2f}%")
    st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(str(e))
