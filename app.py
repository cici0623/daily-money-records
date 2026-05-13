import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, datetime
import os
import json
import urllib.request

st.set_page_config(
    page_title="cici’s money track",
    page_icon="💗",
    layout="wide"
)

def login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "current_user" not in st.session_state:
        st.session_state["current_user"] = ""

    if st.session_state["logged_in"]:
        return True

    st.markdown(
        """
        <div style="
            max-width: 520px;
            margin: 120px auto 20px auto;
            padding: 36px;
            border-radius: 28px;
            background: linear-gradient(135deg, #fff7ef 0%, #fff1f6 100%);
            border: 1px solid rgba(230, 190, 195, 0.6);
            box-shadow: 0 18px 42px rgba(210, 150, 160, 0.16);
        ">
            <div style="font-size: 34px; font-weight: 850; color: #333333;">
                cici’s money track
            </div>
            <div style="font-size: 14px; color: #777777; margin-top: 8px;">
                Login to open your own money book.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = st.secrets.get("users", {})

        if username in users and password == users[username]:
            st.session_state["logged_in"] = True
            st.session_state["current_user"] = username
            st.rerun()
        else:
            st.error("Wrong username or password.")

    return False


if not login():
    st.stop()

DATA_FILE = "records.csv"
BUDGET_FILE = "budget_settings.json"

# =========================
# CSS
# =========================

st.markdown(
    """
    <style>
    [data-testid="stHeader"] {
        background: rgba(255, 248, 241, 0.88);
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(255, 220, 230, 0.22), transparent 28%),
            radial-gradient(circle at bottom left, rgba(255, 231, 205, 0.20), transparent 26%),
            #fff8f1;
        color: #333333;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 4.8rem;
        padding-bottom: 3rem;
    }

    .page-title {
        font-size: 42px;
        font-weight: 850;
        color: #333333;
        letter-spacing: -0.8px;
        margin-bottom: 4px;
    }

    .rate-box {
        text-align: right;
        font-size: 11.5px;
        color: #7d7777;
        line-height: 1.45;
        margin-top: 4px;
    }

    .section-title {
        font-size: 34px;
        font-weight: 860;
        margin-top: 38px;
        margin-bottom: 18px;
        color: #333333;
        letter-spacing: -0.6px;
    }

    .recorded-box {
        background: linear-gradient(135deg, #edfff2 0%, #fffaf5 100%);
        border: 1px solid rgba(120, 200, 150, 0.40);
        color: #3f7a52;
        border-radius: 22px;
        padding: 14px 18px;
        margin-top: 12px;
        margin-bottom: 18px;
        font-size: 15px;
        font-weight: 700;
        box-shadow: 0 8px 22px rgba(120, 180, 140, 0.12);
    }

    div[data-testid="stFormSubmitButton"] {
        display: none;
    }

    /* =========================
       Record big container
    ========================= */

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.record-shell-marker) {
        background:
            radial-gradient(circle at top right, rgba(255, 211, 225, 0.72), transparent 28%),
            radial-gradient(circle at bottom left, rgba(255, 221, 180, 0.55), transparent 24%),
            linear-gradient(135deg, #fff7ef 0%, #fff1f6 100%) !important;
        border: 1px solid rgba(230, 190, 195, 0.60) !important;
        border-radius: 32px !important;
        box-shadow: 0 18px 42px rgba(210, 150, 160, 0.14) !important;
        padding: 28px !important;
        margin-bottom: 34px !important;
        position: relative;
        overflow: hidden;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.record-shell-marker)::after {
        content: "✦";
        position: absolute;
        right: 28px;
        top: 20px;
        font-size: 28px;
        color: #f3a7bb;
    }

    .record-shell-marker {
        display: none;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.record-shell-marker) .character-card {
        box-shadow: none;
        border-radius: 26px;
        margin-bottom: 22px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.record-shell-marker) div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* =========================
       Character cards
    ========================= */

    .character-card {
        display: flex;
        align-items: center;
        gap: 20px;
        background:
            radial-gradient(circle at top right, rgba(255, 210, 225, 0.52), transparent 30%),
            linear-gradient(135deg, #fff7ef 0%, #fff1f6 100%);
        border: 1px solid rgba(230, 210, 205, 0.58);
        border-radius: 30px;
        padding: 22px 24px;
        margin-bottom: 24px;
        box-shadow: 0 14px 34px rgba(220, 170, 170, 0.13);
        position: relative;
        overflow: hidden;
    }

    .character-card::before {
        content: "";
        position: absolute;
        width: 90px;
        height: 90px;
        left: -28px;
        bottom: -28px;
        border-radius: 50%;
        background: rgba(255, 228, 190, 0.36);
    }

    .character-avatar {
        width: 100px;
        height: 100px;
        flex-shrink: 0;
        position: relative;
    }

    .bear-head,
    .dog-head {
        width: 88px;
        height: 80px;
        border-radius: 46% 46% 42% 42%;
        position: absolute;
        left: 6px;
        top: 13px;
        box-shadow: inset 0 -8px 0 rgba(255,255,255,0.25);
    }

    .bear-head {
        background: #f4c28b;
    }

    .dog-head {
        background: #f5c6a5;
    }

    .bear-ear,
    .dog-ear {
        position: absolute;
        width: 30px;
        height: 30px;
        top: 4px;
        border-radius: 50%;
        z-index: 0;
    }

    .bear-ear.left {
        left: 6px;
        background: #eeb77f;
    }

    .bear-ear.right {
        right: 6px;
        background: #eeb77f;
    }

    .dog-ear.left {
        left: 0px;
        top: 20px;
        width: 27px;
        height: 50px;
        border-radius: 50% 40% 55% 45%;
        background: #b77955;
        transform: rotate(18deg);
    }

    .dog-ear.right {
        right: 0px;
        top: 20px;
        width: 27px;
        height: 50px;
        border-radius: 40% 50% 45% 55%;
        background: #b77955;
        transform: rotate(-18deg);
    }

    .eye {
        position: absolute;
        width: 8px;
        height: 10px;
        background: #3a2b25;
        border-radius: 50%;
        top: 35px;
    }

    .eye.left {
        left: 28px;
    }

    .eye.right {
        right: 28px;
    }

    .blush {
        position: absolute;
        width: 14px;
        height: 8px;
        background: rgba(255, 135, 150, 0.45);
        border-radius: 50%;
        top: 48px;
    }

    .blush.left {
        left: 16px;
    }

    .blush.right {
        right: 16px;
    }

    .muzzle {
        position: absolute;
        width: 36px;
        height: 26px;
        background: rgba(255, 245, 230, 0.88);
        border-radius: 50%;
        left: 26px;
        top: 45px;
    }

    .nose {
        position: absolute;
        width: 10px;
        height: 7px;
        background: #3a2b25;
        border-radius: 50%;
        left: 39px;
        top: 48px;
        z-index: 2;
    }

    .mouth {
        position: absolute;
        width: 18px;
        height: 10px;
        border-bottom: 2px solid #3a2b25;
        border-radius: 50%;
        left: 35px;
        top: 54px;
        z-index: 2;
    }

    .tongue {
        position: absolute;
        width: 10px;
        height: 12px;
        background: #ff8fa3;
        border-radius: 0 0 8px 8px;
        left: 39px;
        top: 61px;
        z-index: 2;
    }

    .character-text {
        flex: 1;
        position: relative;
        z-index: 2;
    }

    .character-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.4px;
        color: #8b6b6b;
        background: rgba(255,255,255,0.70);
        border: 1px solid rgba(230, 210, 205, 0.60);
        border-radius: 999px;
        padding: 5px 12px;
        margin-bottom: 9px;
    }

    .character-title {
        font-size: 28px;
        font-weight: 860;
        color: #333333;
        margin-bottom: 5px;
        letter-spacing: -0.4px;
    }

    .character-desc {
        font-size: 14px;
        color: #666666;
        line-height: 1.6;
    }

    .character-sparkle {
        position: relative;
        z-index: 2;
        font-size: 24px;
        color: #f3a7bb;
        align-self: flex-start;
    }

    /* =========================
       Donut cards
    ========================= */

    .donut-card {
        position: relative;
        background:
            radial-gradient(circle at top right, rgba(255, 224, 230, 0.50), transparent 26%),
            linear-gradient(180deg, #fffaf6 0%, #fff4f4 100%);
        border-radius: 26px;
        padding: 22px 14px 20px 14px;
        text-align: center;
        border: 1px solid rgba(230, 210, 205, 0.58);
        box-shadow: 0 12px 28px rgba(216, 169, 169, 0.10);
        overflow: hidden;
    }

    .donut-card::after {
        content: "";
        position: absolute;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(255, 232, 200, 0.42);
        bottom: -28px;
        left: -22px;
    }

    .donut-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        position: relative;
        z-index: 2;
    }

    .donut-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 760;
        color: #8b6b6b;
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(230, 210, 205, 0.55);
        border-radius: 999px;
        padding: 4px 9px;
    }

    .donut-sticker {
        font-size: 24px;
        filter: drop-shadow(0 3px 4px rgba(160, 120, 120, 0.12));
    }

    .donut {
        width: 122px;
        height: 122px;
        margin: 0 auto 14px auto;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.45);
        z-index: 2;
    }

    .donut::before {
        content: "";
        position: absolute;
        width: 80px;
        height: 80px;
        background: #fffaf6;
        border-radius: 50%;
        box-shadow: inset 0 2px 8px rgba(190, 150, 150, 0.08);
    }

    .donut-text {
        position: relative;
        z-index: 1;
        font-weight: 820;
        font-size: 18px;
        color: #333333;
    }

    .donut-label {
        position: relative;
        z-index: 2;
        font-size: 16px;
        font-weight: 780;
        margin-top: 6px;
    }

    .donut-amount {
        position: relative;
        z-index: 2;
        font-size: 21px;
        font-weight: 820;
        margin-top: 6px;
    }

    .donut-mini-line {
        width: 34px;
        height: 4px;
        border-radius: 99px;
        margin: 12px auto 0 auto;
        opacity: 0.85;
    }

    /* =========================
       Budget big container
    ========================= */

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.budget-shell-marker) {
        background:
            radial-gradient(circle at top right, rgba(255, 211, 225, 0.78), transparent 28%),
            radial-gradient(circle at bottom left, rgba(255, 221, 180, 0.70), transparent 24%),
            linear-gradient(135deg, #fff7ef 0%, #fff0f6 100%) !important;
        border: 1px solid rgba(230, 190, 195, 0.60) !important;
        border-radius: 32px !important;
        box-shadow: 0 18px 42px rgba(210, 150, 160, 0.16) !important;
        padding: 28px !important;
        position: relative;
        overflow: hidden;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.budget-shell-marker)::after {
        content: "✦";
        position: absolute;
        right: 28px;
        top: 18px;
        font-size: 28px;
        color: #f3a7bb;
    }

    .budget-shell-marker {
        display: none;
    }

    .budget-top-title {
        font-size: 24px;
        font-weight: 860;
        color: #333333;
        margin-bottom: 18px;
        letter-spacing: -0.4px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.budget-card-marker),
    .budget-card-box {
        background: rgba(255, 255, 255, 0.42) !important;
        backdrop-filter: blur(6px);
        border: 1px solid rgba(230, 205, 205, 0.65) !important;
        border-radius: 24px !important;
        padding: 18px !important;
        box-shadow: 0 8px 22px rgba(200, 150, 150, 0.10);
        min-height: 145px;
    }

    .budget-card-marker {
        display: none;
    }

    .budget-card-label {
        font-size: 12px;
        color: #8a6f6f;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .budget-card-value {
        font-size: 34px;
        font-weight: 880;
        color: #333333;
        line-height: 1.1;
    }

    .budget-input-hint {
        font-size: 12px;
        color: #8a7a7a;
        margin-top: 8px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.budget-shell-marker) input {
        font-size: 34px !important;
        font-weight: 850 !important;
        color: #333333 !important;
        height: 58px !important;
        border-radius: 18px !important;
        background: rgba(255, 255, 255, 0.60) !important;
        border: 1px solid rgba(230, 205, 205, 0.65) !important;
    }

    .budget-bar-bg {
        height: 18px;
        background: rgba(255,255,255,0.72);
        border-radius: 999px;
        overflow: hidden;
        border: 1px solid rgba(230, 205, 205, 0.55);
        margin-top: 22px;
    }

    .budget-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #f7a8b8, #ffcf9f, #ffd6e0);
        background-size: 200% 100%;
        animation: moveGradient 2.8s linear infinite;
    }

    @keyframes moveGradient {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    .budget-status {
        margin-top: 18px;
        padding: 15px 18px;
        border-radius: 20px;
        font-weight: 780;
        font-size: 15px;
    }

    .budget-good {
        background: rgba(234, 255, 241, 0.82);
        color: #3f7a52;
        border: 1px solid rgba(120, 200, 150, 0.45);
    }

    .budget-warning {
        background: rgba(255, 244, 216, 0.90);
        color: #8a6720;
        border: 1px solid rgba(220, 170, 80, 0.45);
    }

    .budget-danger {
        background: rgba(255, 226, 226, 0.90);
        color: #a33a3a;
        border: 1px solid rgba(220, 90, 90, 0.45);
    }

    .stButton > button {
        border-radius: 14px;
        height: 44px;
        font-weight: 780;
        background: linear-gradient(135deg, #f7a8b8 0%, #ef91a6 100%);
        color: white;
        border: none;
        box-shadow: 0 8px 18px rgba(239, 145, 166, 0.18);
    }

    .stButton > button:hover {
        color: white;
        border: none;
        filter: brightness(1.02);
    }

    [data-testid="stVegaLiteChart"] {
        background: transparent !important;
        border-radius: 22px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Categories
# =========================

EXPENSE_CATEGORIES = {
    "🛒 Grocery": ["Not sure", "Fruit", "Vegetables", "Meat", "Snacks", "Milk", "Yogurt"],
    "🚇 Transport": ["Not sure", "Bus", "Subway", "Taxi"],
    "🛍️ Shopping": ["Not sure", "Clothes", "Jewelry", "Shoes", "Bags", "Other"],
    "📚 Study": ["Not sure", "Courses", "Tools", "Exams", "Other"],
    "🧴 Living": ["Not sure", "Daily Supplies", "Laundry", "Utilities", "Other"],
    "🏠 Rent": ["Not sure", "Rent", "Utilities", "Other"],
    "✈️ Travel": ["Not sure", "Flights", "Hotels", "Food", "Other"],
    "🎬 Entertainment": ["Not sure", "Dining Out", "Movies", "Games", "Coffee & Desserts", "Other"],
    "🌙 Other": ["Not sure", "Other"]
}

INCOME_CATEGORIES = ["💸 Allowance", "↩️ Refund"]
ALL_CATEGORIES = list(EXPENSE_CATEGORIES.keys()) + INCOME_CATEGORIES

COLUMNS = [
    "username",
    "date",
    "type",
    "category",
    "subcategory",
    "amount",
    "currency",
    "usd_amount",
    "cny_amount",
    "rate",
    "note",
    "created_at"
]

# =========================
# Helper functions
# =========================

def format_money(value, currency):
    sign = "-" if value < 0 else ""
    value = abs(value)

    if currency == "USD":
        return f"{sign}${value:,.2f}"
    return f"{sign}¥{value:,.2f}"


def signed_amount(value, record_type):
    return value if record_type == "Income" else -value


def parse_amount(text):
    try:
        cleaned = str(text).strip().replace(",", "")
        return float(cleaned)
    except ValueError:
        return None


@st.cache_data(ttl=3600)
def get_live_rate():
    fallback_rate = 7.20
    url = "https://open.er-api.com/v6/latest/USD"

    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

        rate = float(data["rates"]["CNY"])
        updated = data.get("time_last_update_utc", "unknown time")
        return rate, updated

    except Exception:
        return fallback_rate, "API unavailable, fallback rate used"


def convert_amount(amount, source_currency, rate):
    if source_currency == "USD":
        usd_amount = amount
        cny_amount = amount * rate
    else:
        cny_amount = amount
        usd_amount = amount / rate

    return usd_amount, cny_amount


def get_display_amount(row, display_currency):
    return row["usd_amount"] if display_currency == "USD" else row["cny_amount"]


def clean_category_name(category):
    parts = str(category).split(" ", 1)
    if len(parts) == 2:
        return parts[1]
    return str(category)


def create_empty_data_file():
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)


def load_data():
    if not os.path.exists(DATA_FILE):
        create_empty_data_file()

    df = pd.read_csv(DATA_FILE)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLUMNS]

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["usd_amount"] = pd.to_numeric(df["usd_amount"], errors="coerce").fillna(0)
        df["cny_amount"] = pd.to_numeric(df["cny_amount"], errors="coerce").fillna(0)
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce").fillna(0)

    return df


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


def load_budget():
    if not os.path.exists(BUDGET_FILE):
        return {"USD": 800.0, "CNY": 5800.0}

    try:
        with open(BUDGET_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"USD": 800.0, "CNY": 5800.0}


def save_budget(budget):
    with open(BUDGET_FILE, "w") as file:
        json.dump(budget, file)


def handle_budget_change():
    raw = st.session_state.get("budget_inline_input", "")
    new_budget = parse_amount(raw)

    if new_budget is None or new_budget < 0:
        st.session_state["budget_notice"] = ("error", "Please enter a valid budget.")
        return

    currency = st.session_state.get("budget_input_currency", "USD")
    current_rate = st.session_state.get("current_rate", 7.20)

    current_budget = load_budget()
    current_budget[currency] = new_budget

    if currency == "USD":
        current_budget["CNY"] = new_budget * current_rate
    else:
        current_budget["USD"] = new_budget / current_rate

    save_budget(current_budget)

    st.session_state["budget_notice"] = (
        "success",
        f"Budget updated: {format_money(new_budget, currency)}"
    )


def get_month_filtered_data(df, month_filter):
    if df.empty:
        return df

    today = date.today()
    dates = pd.to_datetime(df["date"], errors="coerce")

    if month_filter == "This Month":
        return df[
            (dates.dt.year == today.year) &
            (dates.dt.month == today.month)
        ]

    if month_filter == "Last Month":
        if today.month == 1:
            target_month = 12
            target_year = today.year - 1
        else:
            target_month = today.month - 1
            target_year = today.year

        return df[
            (dates.dt.year == target_year) &
            (dates.dt.month == target_month)
        ]

    return df


def donut_card(label, value_text, percent, color, sticker, badge):
    safe_percent = max(0, min(float(percent), 100))

    html = (
        '<div class="donut-card">'
        '<div class="donut-top">'
        f'<div class="donut-badge">{badge}</div>'
        f'<div class="donut-sticker">{sticker}</div>'
        '</div>'
        f'<div class="donut" style="background: conic-gradient({color} {safe_percent}%, #eee5df 0);">'
        f'<div class="donut-text">{safe_percent:.1f}%</div>'
        '</div>'
        f'<div class="donut-label">{label}</div>'
        f'<div class="donut-amount">{value_text}</div>'
        f'<div class="donut-mini-line" style="background-color:{color};"></div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def render_bear_card():
    html = (
        '<div class="character-card">'
        '<div class="character-avatar">'
        '<div class="bear-ear left"></div>'
        '<div class="bear-ear right"></div>'
        '<div class="bear-head">'
        '<div class="eye left"></div>'
        '<div class="eye right"></div>'
        '<div class="blush left"></div>'
        '<div class="blush right"></div>'
        '<div class="muzzle"></div>'
        '<div class="nose"></div>'
        '<div class="mouth"></div>'
        '</div>'
        '</div>'
        '<div class="character-text">'
        '<div class="character-badge">BEAR MISSION</div>'
        '<div class="character-title">how much did u spend</div>'
        '<div class="character-desc">Type the amount and press Enter. Big category is enough if you do not remember every detail.</div>'
        '</div>'
        '<div class="character-sparkle">✦</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_dog_card():
    html = (
        '<div class="character-card">'
        '<div class="character-avatar">'
        '<div class="dog-ear left"></div>'
        '<div class="dog-ear right"></div>'
        '<div class="dog-head">'
        '<div class="eye left"></div>'
        '<div class="eye right"></div>'
        '<div class="blush left"></div>'
        '<div class="blush right"></div>'
        '<div class="muzzle"></div>'
        '<div class="nose"></div>'
        '<div class="mouth"></div>'
        '<div class="tongue"></div>'
        '</div>'
        '</div>'
        '<div class="character-text">'
        '<div class="character-badge">PUPPY REMINDER</div>'
        '<div class="character-title">Gotta control yourself</div>'
        '<div class="character-desc">A quick check of your money mood this month.</div>'
        '</div>'
        '<div class="character-sparkle">♡</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# =========================
# Load data
# =========================

df = load_data()
rate, updated_time = get_live_rate()
budget = load_budget()

current_user = st.session_state["current_user"]

user_df = df[df["username"] == current_user].copy()

if "last_record_message" not in st.session_state:
    st.session_state["last_record_message"] = ""

if "budget_notice" not in st.session_state:
    st.session_state["budget_notice"] = None

# =========================
# Header
# =========================

header_left, header_right = st.columns([2.1, 1])

with header_left:
    st.markdown('<div class="page-title">cici’s money track</div>', unsafe_allow_html=True)

with header_right:
    display_currency = st.radio("Display Currency", ["USD", "CNY"], horizontal=True)
    st.markdown(
        f'<div class="rate-box">1 USD ≈ {rate:.4f} CNY<br>Updated: {updated_time}</div>',
        unsafe_allow_html=True
    )
    st.caption(f"Logged in as: {current_user}")

# =========================
# Prepare monthly data
# =========================

monthly_df = get_month_filtered_data(user_df, "This Month")

if monthly_df.empty:
    monthly_income = 0.0
    monthly_expense = 0.0
else:
    monthly_income = monthly_df[monthly_df["type"] == "Income"].apply(
        lambda row: get_display_amount(row, display_currency), axis=1
    ).sum()

    monthly_expense = monthly_df[monthly_df["type"] == "Expense"].apply(
        lambda row: get_display_amount(row, display_currency), axis=1
    ).sum()

monthly_balance = monthly_income - monthly_expense
money_flow = monthly_income + monthly_expense

income_percent = (monthly_income / money_flow * 100) if money_flow > 0 else 0
expense_percent = (monthly_expense / money_flow * 100) if money_flow > 0 else 0
saved_percent = (monthly_balance / monthly_income * 100) if monthly_income > 0 else 0
saved_percent = max(0, saved_percent)

# =========================
# 1. Record section
# =========================

with st.container(border=True):
    st.markdown('<span class="record-shell-marker"></span>', unsafe_allow_html=True)

    render_bear_card()

    if st.session_state.get("last_record_message"):
        st.markdown(
            f'<div class="recorded-box">✅ {st.session_state["last_record_message"]}</div>',
            unsafe_allow_html=True
        )

    row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns([1.2, 1, 1.4, 1.4, 1])

    with row1_col1:
        record_date = st.date_input("Date", value=date.today())

    with row1_col2:
        record_type = st.selectbox("Type", ["Expense", "Income"], key="record_type")

    with row1_col3:
        if record_type == "Expense":
            category = st.selectbox("Category", list(EXPENSE_CATEGORIES.keys()), key="expense_category")
        else:
            category = st.selectbox("Category", INCOME_CATEGORIES, key="income_category")

    with row1_col4:
        if record_type == "Expense":
            subcategory = st.selectbox(
                "Subcategory optional",
                EXPENSE_CATEGORIES[category],
                key=f"subcategory_{clean_category_name(category)}"
            )
        else:
            subcategory = "Not needed"
            st.text_input("Subcategory optional", value="Not needed", disabled=True)

    with row1_col5:
        currency = st.selectbox("Currency", ["USD", "CNY"], key="record_currency")

    with st.form("add_record_form", clear_on_submit=True, enter_to_submit=True):
        row2_col1, row2_col2 = st.columns([1.1, 3])

        with row2_col1:
            amount_text = st.text_input("Amount", placeholder="12.50")

        with row2_col2:
            note = st.text_input("Note", placeholder="coffee, subway, groceries...")

        submitted = st.form_submit_button("submit")
        amount = parse_amount(amount_text) if amount_text else None

        if submitted:
            if amount is None:
                st.error("Please enter a valid amount. Example: 12.50")
            elif amount <= 0:
                st.error("Amount must be greater than 0.")
            else:
                usd_amount, cny_amount = convert_amount(amount, currency, rate)

                new_record = pd.DataFrame([{
                    "username": current_user,
                    "date": record_date,
                    "type": record_type,
                    "category": category,
                    "subcategory": subcategory,
                    "amount": amount,
                    "currency": currency,
                    "usd_amount": usd_amount,
                    "cny_amount": cny_amount,
                    "rate": rate,
                    "note": note,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])

                df = pd.concat([df, new_record], ignore_index=True)
                save_data(df)

                display_value = format_money(
                    get_display_amount(new_record.iloc[0], display_currency),
                    display_currency
                )

                st.session_state["last_record_message"] = (
                    f"Recorded! {record_type} · {clean_category_name(category)} · "
                    f"{subcategory} · {display_value}"
                )

                st.toast("Recorded by the little bear", icon="🧸")
                st.rerun()

# =========================
# 2. Main board
# =========================

render_dog_card()

d1, d2, d3 = st.columns(3)

with d1:
    donut_card("Income", format_money(monthly_income, display_currency), income_percent, "#6BCB77", "🍀", "COME IN")

with d2:
    donut_card("Expense", format_money(monthly_expense, display_currency), expense_percent, "#FF6B6B", "🍓", "GO OUT")

with d3:
    donut_card("Balance", format_money(monthly_balance, display_currency), saved_percent, "#4D96FF", "🫧", "STAYING")

# =========================
# 3. Visual analysis
# =========================

st.markdown('<div class="section-title">Where the Money Escaped</div>', unsafe_allow_html=True)

analysis_left, analysis_right = st.columns(2)

with analysis_left:
    st.subheader("Spending Hotspots")

    chart_df = get_month_filtered_data(user_df, "This Month")
    expense_chart_df = chart_df[chart_df["type"] == "Expense"].copy()

    if expense_chart_df.empty:
        st.info("No expense data for this month.")
    else:
        expense_chart_df["display_amount_value"] = expense_chart_df.apply(
            lambda row: get_display_amount(row, display_currency), axis=1
        )
        expense_chart_df["clean_category"] = expense_chart_df["category"].apply(clean_category_name)

        category_chart = (
            expense_chart_df.groupby("clean_category")["display_amount_value"]
            .sum()
            .reset_index()
            .sort_values("display_amount_value", ascending=False)
        )

        bar_chart = (
            alt.Chart(category_chart)
            .mark_bar(cornerRadius=14)
            .encode(
                x=alt.X("display_amount_value:Q", title=None, axis=alt.Axis(grid=False)),
                y=alt.Y("clean_category:N", sort="-x", title=None),
                tooltip=[
                    alt.Tooltip("clean_category:N", title="Category"),
                    alt.Tooltip("display_amount_value:Q", title="Amount", format=",.2f")
                ],
                color=alt.Color(
                    "display_amount_value:Q",
                    scale=alt.Scale(range=["#ffd6e0", "#f7a8b8", "#ef7895"]),
                    legend=None
                )
            )
            .properties(height=330, background="transparent")
            .configure_view(strokeOpacity=0)
            .configure_axis(
                labelColor="#7d7d92",
                titleColor="#7d7d92",
                gridColor="rgba(220, 210, 215, 0.35)"
            )
        )

        st.altair_chart(bar_chart, use_container_width=True)

with analysis_right:
    st.subheader("Daily Spend Wave")

    trend_df = get_month_filtered_data(user_df, "This Month")
    trend_expense_df = trend_df[trend_df["type"] == "Expense"].copy()

    if trend_expense_df.empty:
        st.info("No daily expense data for this month.")
    else:
        trend_expense_df["display_amount_value"] = trend_expense_df.apply(
            lambda row: get_display_amount(row, display_currency), axis=1
        )

        daily_trend = (
            trend_expense_df.groupby("date")["display_amount_value"]
            .sum()
            .reset_index()
        )

        line_chart = (
            alt.Chart(daily_trend)
            .mark_line(point=True, strokeWidth=5, interpolate="monotone")
            .encode(
                x=alt.X("date:T", title=None),
                y=alt.Y("display_amount_value:Q", title=None),
                tooltip=[
                    alt.Tooltip("date:T", title="Date"),
                    alt.Tooltip("display_amount_value:Q", title="Amount", format=",.2f")
                ],
                color=alt.value("#4D96FF")
            )
            .properties(height=330, background="transparent")
            .configure_view(strokeOpacity=0)
            .configure_axis(
                labelColor="#7d7d92",
                titleColor="#7d7d92",
                gridColor="rgba(220, 210, 215, 0.35)"
            )
        )

        st.altair_chart(line_chart, use_container_width=True)

# =========================
# 4. Monthly budget
# =========================

st.markdown('<div class="section-title">Can I survive this month?</div>', unsafe_allow_html=True)

budget_value = float(budget.get(display_currency, 0))
spent = monthly_expense

if budget_value <= 0:
    remaining = 0
    used_percent = 0
    status_class = "budget-warning"
    status_text = "Set a budget to wake up your monthly survival mode."
else:
    remaining = budget_value - spent
    used_percent = spent / budget_value * 100

    if used_percent >= 100:
        status_class = "budget-danger"
        status_text = "You are over budget. The puppy is quietly judging you."
    elif used_percent >= 80:
        status_class = "budget-warning"
        status_text = "Over 80% used. Slow down a little for the rest of this month."
    else:
        status_class = "budget-good"
        status_text = "You are still in control this month."

progress_percent = min(max(used_percent, 0), 100)

if st.session_state.get("budget_input_active_currency") != display_currency:
    st.session_state["budget_inline_input"] = str(round(budget_value, 2))
    st.session_state["budget_input_active_currency"] = display_currency

st.session_state["budget_input_currency"] = display_currency
st.session_state["current_rate"] = rate

with st.container(border=True):
    st.markdown('<span class="budget-shell-marker"></span>', unsafe_allow_html=True)
    st.markdown('<div class="budget-top-title">Monthly Survival Check</div>', unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        with st.container(border=True):
            st.markdown('<span class="budget-card-marker"></span>', unsafe_allow_html=True)
            st.markdown('<div class="budget-card-label">BUDGET</div>', unsafe_allow_html=True)

            st.text_input(
                "Budget",
                key="budget_inline_input",
                label_visibility="collapsed",
                on_change=handle_budget_change
            )

            st.markdown('<div class="budget-input-hint">Press Enter to save</div>', unsafe_allow_html=True)

    with b2:
        st.markdown(
            (
                '<div class="budget-card-box">'
                '<div class="budget-card-label">SPENT</div>'
                f'<div class="budget-card-value">{format_money(spent, display_currency)}</div>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    with b3:
        st.markdown(
            (
                '<div class="budget-card-box">'
                '<div class="budget-card-label">LEFT</div>'
                f'<div class="budget-card-value">{format_money(remaining, display_currency)}</div>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    with b4:
        st.markdown(
            (
                '<div class="budget-card-box">'
                '<div class="budget-card-label">USED</div>'
                f'<div class="budget-card-value">{used_percent:.1f}%</div>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    st.markdown(
        (
            '<div class="budget-bar-bg">'
            f'<div class="budget-bar-fill" style="width:{progress_percent}%;"></div>'
            '</div>'
        ),
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="budget-status {status_class}">{status_text}</div>',
        unsafe_allow_html=True
    )

if st.session_state["budget_notice"]:
    notice_type, notice_text = st.session_state["budget_notice"]

    if notice_type == "success":
        st.success(notice_text)
    else:
        st.error(notice_text)

# =========================
# 5. Bank statement
# =========================

with st.expander("Bank Statement", expanded=False):
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)

    with filter_col1:
        month_filter = st.selectbox("Month", ["This Month", "Last Month", "All"])

    with filter_col2:
        type_filter = st.selectbox("Type", ["All", "Expense", "Income"])

    filtered_df = get_month_filtered_data(user_df, month_filter)

    if type_filter != "All":
        filtered_df = filtered_df[filtered_df["type"] == type_filter]

    if type_filter == "Expense":
        category_options = ["All"] + list(EXPENSE_CATEGORIES.keys())
    elif type_filter == "Income":
        category_options = ["All"] + INCOME_CATEGORIES
    else:
        category_options = ["All"] + ALL_CATEGORIES

    with filter_col3:
        category_filter = st.selectbox("Category Filter", category_options)

    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    if type_filter == "Income":
        subcategory_options = ["All"]
    else:
        if category_filter in EXPENSE_CATEGORIES:
            subcategory_options = ["All"] + EXPENSE_CATEGORIES[category_filter]
        else:
            all_subcategories = sorted(
                list({item for sublist in EXPENSE_CATEGORIES.values() for item in sublist})
            )
            subcategory_options = ["All"] + all_subcategories

    with filter_col4:
        subcategory_filter = st.selectbox("Subcategory Filter", subcategory_options)

    if subcategory_filter != "All":
        filtered_df = filtered_df[filtered_df["subcategory"] == subcategory_filter]

    with filter_col5:
        sort_filter = st.selectbox(
            "Sort",
            ["Newest First", "Oldest First", "Highest Amount", "Lowest Amount"]
        )

    if not filtered_df.empty:
        filtered_df = filtered_df.copy()
        filtered_df["display_amount_value"] = filtered_df.apply(
            lambda row: get_display_amount(row, display_currency), axis=1
        )

        if sort_filter == "Newest First":
            filtered_df = filtered_df.sort_values("date", ascending=False)
        elif sort_filter == "Oldest First":
            filtered_df = filtered_df.sort_values("date", ascending=True)
        elif sort_filter == "Highest Amount":
            filtered_df = filtered_df.sort_values("display_amount_value", ascending=False)
        elif sort_filter == "Lowest Amount":
            filtered_df = filtered_df.sort_values("display_amount_value", ascending=True)

    if filtered_df.empty:
        st.info("No transactions yet.")
    else:
        display_table = filtered_df.copy()

        display_table["Amount"] = display_table.apply(
            lambda row: format_money(
                signed_amount(get_display_amount(row, display_currency), row["type"]),
                display_currency
            ),
            axis=1
        )

        display_table["Original"] = display_table.apply(
            lambda row: f"{format_money(signed_amount(row['amount'], row['type']), row['currency'])} {row['currency']}",
            axis=1
        )

        display_table["Category"] = display_table["category"].apply(clean_category_name)

        display_table = display_table.rename(columns={
            "date": "Date",
            "type": "Type",
            "subcategory": "Subcategory",
            "note": "Note"
        })

        st.dataframe(
            display_table[
                ["Date", "Type", "Category", "Subcategory", "Amount", "Original", "Note"]
            ],
            width="stretch",
            hide_index=True
        )

    if st.button("Clear My Records"):
        df = df[df["username"] != current_user].copy()
        save_data(df)
        st.success("Your records have been cleared.")
        st.rerun()
