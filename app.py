"""
================================================================================
PROJECT: CampusPocket Pro (Student Expenditure Analytics)
FEATURES:
  - Real Email & Password Authentication (Supabase Cloud + Local Hashed Engine)
  - Isolated Student Profiles & Individual Dashboards
  - 15 Standard Student Expenditure Categories
  - Dynamic 4-Metric Ribbon & Top Horizontal Navigation (No Left Sidebar)
  - Interactive Plotly Visualizations (Trend, Donut, Weekly Bar, Gauge)
  - Full CRUD: Add, Search, Filter, In-Place Edit, and Delete Transactions
  - Institutional Analytics & CSV Export
================================================================================
"""

import os
import re
import json
import hashlib
from datetime import datetime, date
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
# 1. PAGE SETUP & THEME INJECTION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="CampusPocket Pro | Student Finance Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DARK_THEME_CSS = """
<style>
    /* Suppress native Streamlit left sidebar */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Base Canvas */
    .stApp {
        background-color: #070B14;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Top Brand & Session Header */
    .brand-title {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 0.5px;
        background: linear-gradient(90deg, #00F5D4 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-tag {
        font-size: 11px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    /* Horizontal Nav Bar Pills */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        background-color: #0B1120 !important;
        padding: 6px 10px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background: transparent !important;
        border: 1px solid transparent !important;
        padding: 7px 16px !important;
        border-radius: 8px !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        margin-right: 0px !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        color: #00F5D4 !important;
        background: rgba(0, 245, 212, 0.06) !important;
        border-color: rgba(0, 245, 212, 0.2) !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        background: rgba(0, 245, 212, 0.12) !important;
        color: #00F5D4 !important;
        border-color: #00F5D4 !important;
        box-shadow: 0 0 12px rgba(0, 245, 212, 0.3) !important;
    }

    /* 4 Primary Summary Cards */
    .summary-card {
        background: #0E1626;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }
    .summary-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 245, 212, 0.4);
        box-shadow: 0 6px 20px rgba(0, 245, 212, 0.15);
    }
    .summary-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .summary-title {
        font-size: 12px;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .summary-icon {
        font-size: 20px;
        padding: 8px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .summary-value {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
        color: #F8FAFC;
    }
    .summary-subtext {
        font-size: 12px;
        color: #64748B;
        font-weight: 500;
    }

    /* Accent Value Colors */
    .val-teal { color: #00F5D4 !important; text-shadow: 0 0 12px rgba(0, 245, 212, 0.35); }
    .val-green { color: #10B981 !important; text-shadow: 0 0 12px rgba(16, 185, 129, 0.35); }
    .val-purple { color: #A78BFA !important; text-shadow: 0 0 12px rgba(167, 139, 250, 0.35); }
    .val-red { color: #EF4444 !important; text-shadow: 0 0 12px rgba(239, 68, 68, 0.35); }

    /* Dashboard Panels */
    .dashboard-panel {
        background: #0E1626;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3);
    }
    .panel-header {
        font-size: 15px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        letter-spacing: 0.3px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 10px;
    }

    /* Auth Box */
    .auth-container {
        max-width: 480px;
        margin: 40px auto;
        background: #0E1626;
        border: 1px solid rgba(0, 245, 212, 0.25);
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 245, 212, 0.1);
    }
    .auth-title {
        text-align: center;
        font-size: 24px;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 6px;
    }
    .auth-subtitle {
        text-align: center;
        font-size: 13px;
        color: #94A3B8;
        margin-bottom: 24px;
    }

    /* Custom Form & Input Styles for Dark Theme */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #070D18 !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    input, select, textarea {
        color: #F8FAFC !important;
    }

    /* Button Enhancements */
    button[kind="primary"], div.stButton > button:first-child {
        background: linear-gradient(135deg, #00F5D4 0%, #10B981 100%) !important;
        color: #070B14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 9px 20px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 10px rgba(0, 245, 212, 0.25) !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 18px rgba(0, 245, 212, 0.45) !important;
        color: #000000 !important;
    }

    /* Progress bar custom color */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00F5D4 0%, #10B981 100%) !important;
    }
</style>
"""
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. CONSTANTS & SYSTEM CONFIGURATION
# ------------------------------------------------------------------------------
SAMPLE_FILE = "sample_expenses.csv"
USERS_DB_FILE = "local_users.json"
STORAGE_DIR = "user_vaults"
os.makedirs(STORAGE_DIR, exist_ok=True)

ALL_CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Transportation",
    "Education & Study Materials",
    "Accommodation & Rent",
    "Shopping & Clothing",
    "Entertainment",
    "Alcohol",
    "Health & Medical Expenses",
    "Personal Care & Hygiene",
    "Mobile & Internet",
    "Subscriptions",
    "Travel",
    "College Fees",
    "Miscellaneous / Others"
]

PAYMENT_METHODS = ["UPI", "Cash", "Card", "Net Banking"]

PALETTE = [
    "#00F5D4", "#10B981", "#7C3AED", "#6366F1", "#F59E0B",
    "#EC4899", "#3B82F6", "#14F195", "#8B5CF6", "#06D6A0",
    "#EF4444", "#38BDF8", "#F97316", "#A855F7", "#64748B"
]

# ------------------------------------------------------------------------------
# 3. SUPABASE CLIENT & LOCAL AUTH ENGINE
# ------------------------------------------------------------------------------
@st.cache_resource
def init_supabase():
    """Initializes cloud Supabase client if credentials exist in secrets."""
    try:
        from supabase import create_client, Client
        sb_url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
        sb_key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY"))
        if sb_url and sb_key and "your-project" not in sb_url:
            return create_client(sb_url, sb_key)
    except Exception:
        pass
    return None

supabase_client = init_supabase()

def hash_password(password: str) -> str:
    """Computes SHA-256 hash for secure local credential storage."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_local_users() -> dict:
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_local_users(users_dict: dict):
    with open(USERS_DB_FILE, "w") as f:
        json.dump(users_dict, f, indent=2)

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email.strip()))

# ------------------------------------------------------------------------------
# 4. USER-SCOPED STORAGE MANAGEMENT
# ------------------------------------------------------------------------------
def get_user_file_paths(user_id: str):
    """Returns unique, isolated storage paths for the authenticated student."""
    sanitized = re.sub(r"[^\w\.-]", "_", user_id)
    exp_path = os.path.join(STORAGE_DIR, f"expenses_{sanitized}.csv")
    budget_path = os.path.join(STORAGE_DIR, f"budget_{sanitized}.txt")
    return exp_path, budget_path

def load_user_expenses(user_id: str) -> pd.DataFrame:
    """Loads expenses isolated to the current user."""
    # Cloud Supabase Path
    if supabase_client:
        try:
            res = supabase_client.table("expenses").select("*").eq("user_id", user_id).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['Date'] = pd.to_datetime(df['date']).dt.date
                df['Amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
                df['Category'] = df['category']
                df['Payment Method'] = df['payment_method']
                df['Description'] = df['description']
                df['Notes'] = df['notes'].fillna("")
                df['ID'] = df['id']
                return df[['ID', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Notes']]
        except Exception:
            pass

    # Local Fallback Path (Isolated file per user)
    exp_path, _ = get_user_file_paths(user_id)
    if os.path.exists(exp_path):
        df = pd.read_csv(exp_path)
    elif os.path.exists(SAMPLE_FILE):
        df = pd.read_csv(SAMPLE_FILE)
        df.to_csv(exp_path, index=False)
    else:
        df = pd.DataFrame(columns=["ID", "Date", "Category", "Amount", "Payment Method", "Description", "Notes"])

    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0.0)
        if 'Notes' not in df.columns:
            df['Notes'] = ""
    return df

def save_user_expenses(user_id: str, df: pd.DataFrame):
    """Persists records back to user's isolated storage."""
    exp_path, _ = get_user_file_paths(user_id)
    df.to_csv(exp_path, index=False)

    if supabase_client:
        try:
            supabase_client.table("expenses").delete().eq("user_id", user_id).execute()
            if not df.empty:
                records = []
                for _, r in df.iterrows():
                    records.append({
                        "user_id": user_id,
                        "date": str(r['Date']),
                        "category": r['Category'],
                        "amount": float(r['Amount']),
                        "payment_method": r['Payment Method'],
                        "description": r['Description'],
                        "notes": str(r.get('Notes', ''))
                    })
                supabase_client.table("expenses").insert(records).execute()
        except Exception:
            pass

def load_user_budget(user_id: str) -> float:
    """Loads target monthly budget for user."""
    _, b_path = get_user_file_paths(user_id)
    if os.path.exists(b_path):
        try:
            with open(b_path, "r") as f:
                return float(f.read().strip())
        except Exception:
            return 15000.0
    return 15000.0

def save_user_budget(user_id: str, budget: float):
    """Saves user budget."""
    _, b_path = get_user_file_paths(user_id)
    with open(b_path, "w") as f:
        f.write(str(round(budget, 2)))

# ------------------------------------------------------------------------------
# 5. AUTHENTICATION CONTROLLER (LOGIN / REGISTER)
# ------------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # Render Centered Authentication Card
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="max-width: 480px; margin: 0 auto; text-align: center; padding: 24px 16px 8px;">
            <div class="brand-title" style="justify-content: center; font-size: 24px; margin-bottom: 4px;">
                ⚡ CAMPUSPOCKET PRO
            </div>
            <div class="auth-subtitle">Student Expenditure Analytics & Budget Engine</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])

    # TAB 1: LOGIN
    with auth_tab1:
        with st.form("login_form"):
            login_email = st.text_input("Student College Email", placeholder="student@college.edu")
            login_password = st.text_input("Password", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button("🚀 Access Dashboard", use_container_width=True)

        if submit_login:
            if not login_email.strip() or not login_password.strip():
                st.error("Please provide both email and password.")
            else:
                authenticated = False
                user_payload = None

                # Supabase Auth Attempt
                if supabase_client:
                    try:
                        res = supabase_client.auth.sign_in_with_password({
                            "email": login_email.strip(),
                            "password": login_password
                        })
                        if res.user:
                            user_payload = {"id": res.user.id, "email": res.user.email}
                            authenticated = True
                    except Exception as err:
                        st.error(f"Cloud Auth Error: {str(err)}")

                # Local Vault Authentication Fallback
                if not authenticated:
                    local_users = load_local_users()
                    u_email = login_email.strip().lower()
                    if u_email in local_users:
                        if local_users[u_email]["password"] == hash_password(login_password):
                            user_payload = {"id": local_users[u_email]["id"], "email": u_email}
                            authenticated = True
                        else:
                            st.error("Invalid email or password.")
                    else:
                        st.error("Account not found. Please register or use Examiner Demo Mode below.")

                if authenticated and user_payload:
                    st.session_state.user = user_payload
                    st.success("Authentication successful! Redirecting...")
                    st.rerun()

    # TAB 2: REGISTER
    with auth_tab2:
        with st.form("register_form"):
            reg_email = st.text_input("College Email Address", placeholder="rollno@college.edu")
            reg_pass = st.text_input("Create Password", type="password", placeholder="At least 6 characters")
            reg_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            submit_reg = st.form_submit_button("✨ Register Account", use_container_width=True)

        if submit_reg:
            if not is_valid_email(reg_email):
                st.error("Please enter a valid email address.")
            elif len(reg_pass) < 6:
                st.error("Password must be at least 6 characters long.")
            elif reg_pass != reg_confirm:
                st.error("Passwords do not match.")
            else:
                registered = False
                user_payload = None

                # Supabase Registration
                if supabase_client:
                    try:
                        res = supabase_client.auth.sign_up({
                            "email": reg_email.strip(),
                            "password": reg_pass
                        })
                        if res.user:
                            user_payload = {"id": res.user.id, "email": res.user.email}
                            registered = True
                    except Exception as err:
                        st.error(f"Supabase Error: {str(err)}")

                # Local Engine Registration
                if not registered:
                    local_users = load_local_users()
                    u_email = reg_email.strip().lower()
                    if u_email in local_users:
                        st.error("An account with this email already exists.")
                    else:
                        new_uid = "usr_" + hashlib.md5(u_email.encode()).hexdigest()[:12]
                        local_users[u_email] = {
                            "id": new_uid,
                            "email": u_email,
                            "password": hash_password(reg_pass),
                            "created_at": datetime.now().isoformat()
                        }
                        save_local_users(local_users)
                        user_payload = {"id": new_uid, "email": u_email}
                        registered = True

                if registered and user_payload:
                    st.session_state.user = user_payload
                    st.success("Account created successfully! Launching your workspace...")
                    st.rerun()

    st.markdown("---")
    # Quick Examiner Demo Bypass
    if st.button("🎓 Instant Practical Demo Login (Examiner Mode)", use_container_width=True):
        st.session_state.user = {"id": "demo_student_viva", "email": "student.viva@bba-it.ac.in"}
        st.rerun()

    st.stop()  # Halt execution until authenticated

# ------------------------------------------------------------------------------
# 6. SESSION STATE INITIALIZATION FOR LOGGED-IN STUDENT
# ------------------------------------------------------------------------------
current_user = st.session_state.user

if "expenses_df" not in st.session_state or st.session_state.get("active_user_id") != current_user["id"]:
    st.session_state.expenses_df = load_user_expenses(current_user["id"])
    st.session_state.monthly_budget = load_user_budget(current_user["id"])
    st.session_state.active_user_id = current_user["id"]

# ------------------------------------------------------------------------------
# 7. TOP BRAND HEADER & AUTH STATUS BAR (NO SIDEBAR)
# ------------------------------------------------------------------------------
col_brand, col_status = st.columns([1.8, 1.2])

with col_brand:
    st.markdown(
        """
        <div class="brand-title">
            <span>⚡ CAMPUSPOCKET PRO</span>
            <span class="brand-tag">| Student Expenditure Analytics</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_status:
    curr_date_str = datetime.now().strftime("%d %b %Y")
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(
            f"""
            <div style="text-align: right; color: #94A3B8; font-size: 12px; margin-top: 4px;">
                👤 <strong style="color: #00F5D4;">{current_user['email']}</strong> &bull; 📅 {curr_date_str}
            </div>
            """,
            unsafe_allow_html=True
        )
    with h_col2:
        if st.button("🚪 Logout", key="logout_btn"):
            if supabase_client:
                try:
                    supabase_client.auth.sign_out()
                except Exception:
                    pass
            st.session_state.user = None
            st.session_state.expenses_df = None
            st.rerun()

# Top Horizontal Navigation Tabs
NAV_OPTIONS = [
    "📊 Dashboard",
    "➕ Add Expense",
    "📋 Transactions",
    "🎯 Budget Management",
    "📈 Analytics & Reports",
    "⚙️ Settings"
]

selected_page = st.radio(
    "Navigation Menu",
    NAV_OPTIONS,
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 8. SHARED DYNAMIC CALCULATIONS (4 METRIC CARDS)
# ------------------------------------------------------------------------------
df_all = st.session_state.expenses_df.copy()

if not df_all.empty:
    df_all['YearMonth'] = pd.to_datetime(df_all['Date']).dt.to_period('M').astype(str)
    all_months = sorted(df_all['YearMonth'].unique(), reverse=True)
    current_month_default = all_months[0] if all_months else datetime.today().strftime('%Y-%m')
else:
    df_all['YearMonth'] = []
    all_months = [datetime.today().strftime('%Y-%m')]
    current_month_default = all_months[0]

active_month = current_month_default
monthly_df = df_all[df_all['YearMonth'] == active_month] if not df_all.empty else pd.DataFrame(columns=df_all.columns)

monthly_budget = float(st.session_state.monthly_budget)
total_monthly_expense = float(monthly_df['Amount'].sum()) if not monthly_df.empty else 0.0
remaining_balance = monthly_budget - total_monthly_expense

if not monthly_df.empty:
    days_with_expenses = monthly_df['Date'].nunique()
    daily_average = total_monthly_expense / days_with_expenses if days_with_expenses > 0 else 0.0
else:
    daily_average = 0.0

budget_usage_pct = (total_monthly_expense / monthly_budget * 100) if monthly_budget > 0 else 0.0

# ------------------------------------------------------------------------------
# 9. FOUR MAIN SUMMARY CARDS (DIRECTLY BELOW NAV BAR)
# ------------------------------------------------------------------------------
card_col1, card_col2, card_col3, card_col4 = st.columns(4)

with card_col1:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-card-header">
                <span class="summary-title">Monthly Budget</span>
                <span class="summary-icon">👛</span>
            </div>
            <div class="summary-value val-purple">₹{monthly_budget:,.2f}</div>
            <div class="summary-subtext">Active Target ({active_month})</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with card_col2:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-card-header">
                <span class="summary-title">Total Expense</span>
                <span class="summary-icon">💸</span>
            </div>
            <div class="summary-value val-teal">₹{total_monthly_expense:,.2f}</div>
            <div class="summary-subtext">{len(monthly_df)} logged transactions</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with card_col3:
    if remaining_balance >= 0:
        bal_class = "val-green"
        status_note = f"{100 - budget_usage_pct:.1f}% remaining"
    else:
        bal_class = "val-red"
        status_note = f"Exceeded by ₹{abs(remaining_balance):,.2f}"

    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-card-header">
                <span class="summary-title">Remaining Balance</span>
                <span class="summary-icon">🛡️</span>
            </div>
            <div class="summary-value {bal_class}">₹{remaining_balance:,.2f}</div>
            <div class="summary-subtext">{status_note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with card_col4:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-card-header">
                <span class="summary-title">Daily Average</span>
                <span class="summary-icon">📊</span>
            </div>
            <div class="summary-value val-teal">₹{daily_average:,.2f}</div>
            <div class="summary-subtext">Active spending days: {monthly_df['Date'].nunique() if not monthly_df.empty else 0}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 10. PAGE ROUTING & VIEWS
# ------------------------------------------------------------------------------

# ----------------------------------
# VIEW 1: DASHBOARD
# ----------------------------------
if selected_page == "📊 Dashboard":
    chart_col1, chart_col2 = st.columns([1.1, 0.9])

    with chart_col1:
        st.markdown(
            """
            <div class="dashboard-panel">
                <div class="panel-header">
                    <span>📈 Monthly Spending Trend (Cumulative Curve)</span>
                    <span style="font-size: 11px; color: #00F5D4; font-weight: 600;">ACTIVE PACING</span>
                </div>
            """,
            unsafe_allow_html=True
        )

        if not monthly_df.empty:
            daily_series = monthly_df.groupby('Date')['Amount'].sum().reset_index().sort_values('Date')
            daily_series['Cumulative'] = daily_series['Amount'].cumsum()

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=pd.to_datetime(daily_series['Date']),
                y=daily_series['Cumulative'],
                mode='lines+markers',
                name='Cumulative Spend',
                line=dict(color='#00F5D4', width=3, shape='spline'),
                marker=dict(size=6, color='#10B981', symbol='circle'),
                fill='tozeroy',
                fillcolor='rgba(0, 245, 212, 0.08)',
                hovertemplate="<b>Date:</b> %{x|%d %b %Y}<br><b>Total Spent:</b> ₹%{y:,.2f}<extra></extra>"
            ))

            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', tickfont=dict(color='#94A3B8', size=11)),
                yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', tickfont=dict(color='#94A3B8', size=11), tickprefix='₹'),
                showlegend=False
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No expense data recorded for this month yet.")

        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown(
            """
            <div class="dashboard-panel">
                <div class="panel-header">
                    <span>🍩 Category Breakdown</span>
                    <span style="font-size: 11px; color: #7C3AED; font-weight: 600;">15 CATEGORIES</span>
                </div>
            """,
            unsafe_allow_html=True
        )

        if not monthly_df.empty:
            cat_summary = monthly_df.groupby('Category')['Amount'].sum().reset_index()

            fig_donut = px.pie(
                cat_summary,
                values='Amount',
                names='Category',
                hole=0.62,
                color_discrete_sequence=PALETTE
            )
            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300,
                margin=dict(l=5, r=5, t=10, b=10),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(color='#94A3B8', size=10)),
                annotations=[dict(
                    text=f"<span style='font-size:11px;color:#94A3B8;'>TOTAL</span><br><b style='font-size:16px;color:#00F5D4;'>₹{total_monthly_expense:,.0f}</b>",
                    x=0.5, y=0.5, font_size=12, showarrow=False
                )]
            )
            fig_donut.update_traces(
                textposition='inside',
                textinfo='percent',
                hovertemplate="<b>%{label}</b><br>Spend: ₹%{value:,.2f} (%{percent})"
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No expense data available for donut breakdown.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Panel Row B: Recent Transactions & Budget Overview
    panel_col1, panel_col2 = st.columns([1.1, 0.9])

    with panel_col1:
        st.markdown(
            """
            <div class="dashboard-panel">
                <div class="panel-header">
                    <span>⚡ Recent Transactions (Personal Ledger)</span>
                    <span style="font-size: 11px; color: #64748B;">Latest 5 Logs</span>
                </div>
            """,
            unsafe_allow_html=True
        )

        if not df_all.empty:
            recent_txns = df_all.sort_values(by="Date", ascending=False).head(5)
            for _, r in recent_txns.iterrows():
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05);
                                border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex;
                                justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 700; color: #F1F5F9; font-size: 13px;">{r['Description']}</div>
                            <div style="font-size: 11px; color: #64748B;">{r['Category']} &bull; 💳 {r['Payment Method']} &bull; 📅 {r['Date']}</div>
                        </div>
                        <div style="font-size: 14px; font-weight: 800; color: #00F5D4;">
                            ₹{r['Amount']:,.2f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No transactions logged yet.")

        st.markdown("</div>", unsafe_allow_html=True)

    with panel_col2:
        st.markdown(
            """
            <div class="dashboard-panel">
                <div class="panel-header">
                    <span>🎯 Budget Utilization & Health</span>
                    <span style="font-size: 11px; color: #00F5D4; font-weight: 600;">ACTIVE PACING</span>
                </div>
            """,
            unsafe_allow_html=True
        )

        ratio_capped = min(max(budget_usage_pct / 100.0, 0.0), 1.0)
        st.progress(ratio_capped)

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; margin-top: 12px; margin-bottom: 12px;">
                <div>
                    <span style="font-size: 11px; color: #64748B;">CONSUMPTION</span><br>
                    <strong style="font-size: 18px; color: {'#EF4444' if budget_usage_pct >= 100 else ('#F59E0B' if budget_usage_pct >= 80 else '#00F5D4')};">
                        {budget_usage_pct:.1f}%
                    </strong>
                </div>
                <div>
                    <span style="font-size: 11px; color: #64748B;">ALLOCATED</span><br>
                    <strong style="font-size: 18px; color: #F8FAFC;">₹{monthly_budget:,.2f}</strong>
                </div>
                <div>
                    <span style="font-size: 11px; color: #64748B;">LEFT TO SPEND</span><br>
                    <strong style="font-size: 18px; color: {'#10B981' if remaining_balance >= 0 else '#EF4444'};">
                        ₹{remaining_balance:,.2f}
                    </strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if budget_usage_pct >= 100:
            st.error(f"🚨 **Budget Breached!** You exceeded your allowance by ₹{abs(remaining_balance):,.2f}.")
        elif budget_usage_pct >= 80:
            st.warning(f"⚠️ **Approaching Limit!** You have consumed {budget_usage_pct:.1f}% of your pocket budget.")
        else:
            st.success("✅ **Healthy Spending Velocity:** You are comfortably within your allowance.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Weekly Comparison (Monday to Sunday)
    st.markdown(
        """
        <div class="dashboard-panel">
            <div class="panel-header">
                <span>📊 Weekly Spending Comparison (Monday – Sunday Aggregation)</span>
                <span style="font-size: 11px; color: #10B981; font-weight: 600;">DAY-OF-WEEK ANALYSIS</span>
            </div>
        """,
        unsafe_allow_html=True
    )

    if not df_all.empty:
        df_weekly = df_all.copy()
        df_weekly['DayOfWeek'] = pd.to_datetime(df_weekly['Date']).dt.day_name()
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_grouped = df_weekly.groupby('DayOfWeek')['Amount'].sum().reindex(days_order, fill_value=0.0).reset_index()

        fig_week = px.bar(
            weekday_grouped,
            x='DayOfWeek',
            y='Amount',
            color='Amount',
            color_continuous_scale=[[0, '#0E3B43'], [0.5, '#06D6A0'], [1, '#00F5D4']],
            text_auto='.2s'
        )
        fig_week.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_showscale=False,
            xaxis=dict(title=None, tickfont=dict(color='#94A3B8', size=12), gridcolor='rgba(255, 255, 255, 0.05)'),
            yaxis=dict(title="Total Amount (₹)", tickfont=dict(color='#94A3B8', size=11), gridcolor='rgba(255, 255, 255, 0.05)', tickprefix='₹')
        )
        st.plotly_chart(fig_week, use_container_width=True)
    else:
        st.info("Log transactions to visualize day-of-week spending patterns.")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------
# VIEW 2: ADD EXPENSE
# ----------------------------------
elif selected_page == "➕ Add Expense":
    st.markdown(
        """
        <div class="dashboard-panel">
            <div class="panel-header">
                <span>➕ Log New Student Expenditure</span>
                <span style="font-size: 11px; color: #00F5D4;">VALIDATED RECORD ENTRY</span>
            </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("entry_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            desc = st.text_input("Expense Description / Merchant*", placeholder="e.g., Campus Thali, Bus Pass, Reference Book")
            amount_val = st.number_input("Amount (in ₹)*", min_value=0.0, step=10.0, format="%.2f")
            category_choice = st.selectbox("Expense Category (15 Options)*", ALL_CATEGORIES)

        with col_f2:
            entry_date = st.date_input("Date of Expense*", value=date.today())
            pay_method = st.selectbox("Payment Method*", PAYMENT_METHODS)
            notes = st.text_area("Optional Notes / Reference", placeholder="Optional transaction ID, room share note, etc.")

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("💾 Record Expense to Personal Ledger")

    if submit_btn:
        if amount_val <= 0:
            st.error("❌ Input Error: Expense amount must be strictly greater than ₹0.")
        elif not desc.strip():
            st.error("❌ Input Error: Description / Merchant name cannot be blank.")
        else:
            current_df = st.session_state.expenses_df
            new_id = int(current_df['ID'].max()) + 1 if not current_df.empty else 1

            new_record = pd.DataFrame([{
                "ID": new_id,
                "Date": entry_date,
                "Category": category_choice,
                "Amount": round(amount_val, 2),
                "Payment Method": pay_method,
                "Description": desc.strip(),
                "Notes": notes.strip()
            }])

            st.session_state.expenses_df = pd.concat([current_df, new_record], ignore_index=True)
            save_user_expenses(current_user["id"], st.session_state.expenses_df)
            st.success(f"✅ Added ₹{amount_val:,.2f} under '{category_choice}' to your dashboard!")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------
# VIEW 3: TRANSACTIONS
# ----------------------------------
elif selected_page == "📋 Transactions":
    st.markdown(
        """
        <div class="dashboard-panel">
            <div class="panel-header">
                <span>📋 Comprehensive Ledger & Transaction Management</span>
                <span style="font-size: 11px; color: #00F5D4;">SEARCH • FILTER • EDIT • DELETE</span>
            </div>
        """,
        unsafe_allow_html=True
    )

    df_txns = st.session_state.expenses_df

    if df_txns.empty:
        st.info("No transaction records available.")
    else:
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            search_query = st.text_input("🔍 Search Description", placeholder="Search keyword...")
        with f2:
            cat_filter = st.multiselect("Filter Categories", options=ALL_CATEGORIES, default=[])
        with f3:
            pay_filter = st.multiselect("Payment Mode", options=PAYMENT_METHODS, default=[])
        with f4:
            sort_by = st.selectbox("Sort By", ["Date (Newest First)", "Date (Oldest First)", "Amount (Highest)", "Amount (Lowest)"])

        filtered = df_txns.copy()
        if search_query.strip():
            filtered = filtered[filtered['Description'].str.contains(search_query.strip(), case=False, na=False)]
        if cat_filter:
            filtered = filtered[filtered['Category'].isin(cat_filter)]
        if pay_filter:
            filtered = filtered[filtered['Payment Method'].isin(pay_filter)]

        if sort_by == "Date (Newest First)":
            filtered = filtered.sort_values(by="Date", ascending=False)
        elif sort_by == "Date (Oldest First)":
            filtered = filtered.sort_values(by="Date", ascending=True)
        elif sort_by == "Amount (Highest)":
            filtered = filtered.sort_values(by="Amount", ascending=False)
        elif sort_by == "Amount (Lowest)":
            filtered = filtered.sort_values(by="Amount", ascending=True)

        st.write(f"Showing **{len(filtered)}** of **{len(df_txns)}** transactions:")
        st.dataframe(
            filtered[['ID', 'Date', 'Description', 'Category', 'Amount', 'Payment Method', 'Notes']],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        col_edit, col_del = st.columns(2)

        # In-Place Edit Form
        with col_edit:
            st.subheader("✏️ Edit Existing Transaction")
            edit_id = st.selectbox("Select Transaction ID to Edit", options=df_txns['ID'].tolist(), key="edit_sel")
            selected_row = df_txns[df_txns['ID'] == edit_id].iloc[0]

            with st.form("edit_form"):
                e_desc = st.text_input("Description", value=selected_row['Description'])
                e_amt = st.number_input("Amount (₹)", min_value=0.01, value=float(selected_row['Amount']), step=10.0)
                e_cat = st.selectbox("Category", ALL_CATEGORIES, index=ALL_CATEGORIES.index(selected_row['Category']) if selected_row['Category'] in ALL_CATEGORIES else 0)
                e_pay = st.selectbox("Payment Method", PAYMENT_METHODS, index=PAYMENT_METHODS.index(selected_row['Payment Method']) if selected_row['Payment Method'] in PAYMENT_METHODS else 0)
                e_date = st.date_input("Date", value=selected_row['Date'])
                e_notes = st.text_input("Notes", value=str(selected_row['Notes']) if pd.notna(selected_row['Notes']) else "")

                save_edit_btn = st.form_submit_button("💾 Update Transaction")
                if save_edit_btn:
                    if e_amt <= 0 or not e_desc.strip():
                        st.error("Invalid amount or empty description.")
                    else:
                        st.session_state.expenses_df.loc[st.session_state.expenses_df['ID'] == edit_id, ['Description', 'Amount', 'Category', 'Payment Method', 'Date', 'Notes']] = [
                            e_desc.strip(), round(e_amt, 2), e_cat, e_pay, e_date, e_notes.strip()
                        ]
                        save_user_expenses(current_user["id"], st.session_state.expenses_df)
                        st.success(f"Transaction #{edit_id} updated successfully!")
                        st.rerun()

        # Delete Form with Confirmation
        with col_del:
            st.subheader("🗑️ Delete Transaction")
            del_id = st.selectbox("Select Transaction ID to Delete", options=df_txns['ID'].tolist(), key="del_sel")
            del_row = df_txns[df_txns['ID'] == del_id].iloc[0]
            st.warning(f"⚠️ Delete **{del_row['Description']}** (₹{del_row['Amount']:,.2f}) on {del_row['Date']}?")

            if st.button("Permanently Remove Record", type="primary"):
                st.session_state.expenses_df = df_txns[df_txns['ID'] != del_id].reset_index(drop=True)
                save_user_expenses(current_user["id"], st.session_state.expenses_df)
                st.success(f"Record #{del_id} removed.")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------
# VIEW 4: BUDGET MANAGEMENT
# ----------------------------------
elif selected_page == "🎯 Budget Management":
    st.markdown(
        """
        <div class="dashboard-panel">
            <div class="panel-header">
                <span>🎯 Monthly Budget Allocation & Ceiling Controls</span>
                <span style="font-size: 11px; color: #00F5D4;">ACTIVE CONTROLS</span>
            </div>
        """,
        unsafe_allow_html=True
    )

    b_col1, b_col2 = st.columns([1, 1.2])

    with b_col1:
        st.subheader("Set Monthly Allowance")
        new_budget_input = st.number_input(
            "Target Monthly Budget (₹)",
            min_value=500.0,
            value=float(st.session_state.monthly_budget),
            step=500.0
        )
        if st.button("Update Monthly Budget"):
            st.session_state.monthly_budget = float(new_budget_input)
            save_user_budget(current_user["id"], new_budget_input)
            st.success(f"Budget updated to ₹{new_budget_input:,.2f}!")
            st.rerun()

        st.markdown("---")
        st.markdown("#### Dynamic Budget Rules")
        st.markdown(
            """
            - 🟢 **Safe Pacing (0% – 79%)**: Spending within monthly goals.
            - 🟡 **Warning Zone (80% – 99%)**: Approaching monthly budget threshold.
            - 🔴 **Overspent Alert (100%+)**: Immediate red alert & deficit tracking.
            """
        )

    with b_col2:
        st.subheader("Budget Gauge")
        gauge_val = total_monthly_expense
        max_range = max(monthly_budget * 1.3, gauge_val * 1.1)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=gauge_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': monthly_budget, 'increasing': {'color': "#EF4444"}, 'decreasing': {'color': "#10B981"}},
            gauge={
                'axis': {'range': [0, max_range], 'tickprefix': "₹", 'tickcolor': "#94A3B8"},
                'bar': {'color': "#00F5D4"},
                'bgcolor': "#070B14",
                'borderwidth': 1,
                'bordercolor': "rgba(255, 255, 255, 0.1)",
                'steps': [
                    {'range': [0, monthly_budget * 0.8], 'color': 'rgba(16, 185, 129, 0.2)'},
                    {'range': [monthly_budget * 0.8, monthly_budget], 'color': 'rgba(245, 158, 11, 0.25)'},
                    {'range': [monthly_budget, max_range], 'color': 'rgba(239, 68, 68, 0.3)'}
                ],
                'threshold': {'line': {'color': "#EF4444", 'width': 3}, 'thickness': 0.8, 'value': monthly_budget}
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=280,
            margin=dict(l=20, r=20, t=10, b=10),
            font=dict(color="#F8FAFC")
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------
# VIEW 5: ANALYTICS & REPORTS
# ----------------------------------
elif selected_page == "📈 Analytics & Reports":
    st.markdown(
        """
        <div class="dashboard-panel">
            <div class="panel-header">
                <span>📈 Advanced Analytics & Institutional Expense Reports</span>
                <span style="font-size: 11px; color: #00F5D4;">MONTHLY AUDIT</span>
            </div>
        """,
        unsafe_allow_html=True
    )

    sel_col1, sel_col2 = st.columns([1, 3])
    with sel_col1:
        chosen_month = st.selectbox("Select Month for Report", all_months, index=0)

    scoped_df = df_all[df_all['YearMonth'] == chosen_month] if not df_all.empty else pd.DataFrame(columns=df_all.columns)

    if scoped_df.empty:
        st.info("No records available for the selected month.")
    else:
        m_total = scoped_df['Amount'].sum()
        m_days = scoped_df['Date'].nunique()
        m_daily_avg = m_total / m_days if m_days > 0 else 0.0

        cat_agg = scoped_df.groupby('Category')['Amount'].sum()
        top_cat_name = cat_agg.idxmax()
        top_cat_amt = cat_agg.max()
        max_row = scoped_df.loc[scoped_df['Amount'].idxmax()]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Selected Month Spend", f"₹{m_total:,.2f}")
        k2.metric("Average Daily Burn", f"₹{m_daily_avg:,.2f}")
        k3.metric("Highest Category", f"{top_cat_name}", f"₹{top_cat_amt:,.2f}")
        k4.metric("Largest Single Spend", f"{max_row['Description'][:15]}...", f"₹{max_row['Amount']:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"📊 Category-Wise Aggregate Summary ({chosen_month})")

        cat_table = scoped_df.groupby('Category').agg(
            Total_Spent=('Amount', 'sum'),
            Transactions=('Amount', 'count'),
            Average_Ticket=('Amount', 'mean')
        ).reset_index()

        cat_table['Percentage_Share'] = (cat_table['Total_Spent'] / m_total) * 100
        cat_table = cat_table.sort_values(by='Total_Spent', ascending=False)
        cat_table.columns = ['Category', 'Total Spent (₹)', 'Count', 'Average/Txn (₹)', 'Share (%)']

        st.dataframe(
            cat_table.style.format({
                'Total Spent (₹)': '₹{:,.2f}',
                'Average/Txn (₹)': '₹{:,.2f}',
                'Share (%)': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("📥 Export Personal Ledger")
        csv_bytes = scoped_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download {chosen_month} Report as CSV",
            data=csv_bytes,
            file_name=f"student_expenses_{current_user['id']}_{chosen_month}.csv",
            mime="text/csv"
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------
# VIEW 6: SETTINGS
# ----------------------------------
elif selected_page == "⚙️ Settings":
    st.markdown(
        """
        <div class="dashboard-panel">
            <div class="panel-header">
                <span>⚙️ System Preferences & Student Configuration</span>
                <span style="font-size: 11px; color: #64748B;">SETTINGS</span>
            </div>
        """,
        unsafe_allow_html=True
    )

    s1, s2 = st.columns(2)
    with s1:
        st.subheader("Student Identity")
        st.text_input("Active Authenticated Account", value=current_user["email"], disabled=True)
        st.text_input("User Vault ID", value=current_user["id"], disabled=True)
        st.selectbox("Default Currency Format", ["₹ INR (Indian Rupee)"], index=0, disabled=True)
        st.caption("Standardized to Indian Rupees (₹) for college project guidelines.")

    with s2:
        st.subheader("Monitored Categories (15 Active)")
        for idx, c in enumerate(ALL_CATEGORIES, 1):
            st.markdown(f"<span style='font-size: 12px; color: #00F5D4;'>{idx:02d}.</span> <span style='font-size: 12px; color: #94A3B8;'>{c}</span>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)